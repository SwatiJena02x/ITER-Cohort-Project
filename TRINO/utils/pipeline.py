from __future__ import annotations

import json
import math
import os
import tempfile
from collections import defaultdict
from dataclasses import asdict
from typing import Dict, Iterable, List, Sequence, Tuple

import cv2
import numpy as np
import pandas as pd
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    import pytesseract
except ImportError:
    pytesseract = None
from PIL import Image

from .schema import AnalysisReport, EvidenceChunk, RetrievalHit, VectorStore

REFERENCE_PATTERNS = {
    "phone_activity": "A mobile phone, handheld device, or phone-like object is visible or mentioned in text.",
    "multiple_person": "Multiple faces or persons are present in the camera frame.",
    "absence": "The candidate is absent from the camera view.",
    "attention_deviation": "The candidate repeatedly looks away or deviates attention from the screen.",
    "normal": "The candidate is visible with stable behaviour and low-risk signals."
}
REFERENCE_TEXTS = list(REFERENCE_PATTERNS.values())
REFERENCE_LABELS = list(REFERENCE_PATTERNS.keys())
REFERENCE_VECTORIZER = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
try:
    REFERENCE_MATRIX = REFERENCE_VECTORIZER.fit_transform(REFERENCE_TEXTS)
except:
    REFERENCE_MATRIX = None



EVENT_LABELS: Dict[str, str] = {
    "multiple_person_presence": "possible multiple-person presence",
    "candidate_absence": "candidate absence from camera view",
    "attention_deviation": "repeated attention deviation",
    "suspicious_object_activity": "suspicious object or hand activity",
}

QUERY_HINTS: Dict[str, Sequence[str]] = {
    "phone": ("suspicious_object_activity",),
    "mobile": ("suspicious_object_activity",),
    "device": ("suspicious_object_activity",),
    "person": ("multiple_person_presence",),
    "people": ("multiple_person_presence",),
    "second person": ("multiple_person_presence",),
    "absent": ("candidate_absence",),
    "missing": ("candidate_absence",),
    "away": ("attention_deviation",),
    "look away": ("attention_deviation",),
    "notes": ("suspicious_object_activity",),
}


def format_timecode(seconds: float) -> str:
    total_seconds = max(0, int(seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def _safe_face_detector() -> cv2.CascadeClassifier:
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(cascade_path)
    if detector.empty():
        raise RuntimeError("Could not load the OpenCV face cascade classifier.")
    return detector


def _make_chunk_description(chunk: EvidenceChunk) -> str:
    if not chunk.events:
        return (
            f"{format_timecode(chunk.start_time)} to {format_timecode(chunk.end_time)}: "
            f"candidate visible with stable behaviour and low-risk signals."
        )

    sentences = [
        f"{format_timecode(chunk.start_time)} to {format_timecode(chunk.end_time)}",
        f"{chunk.frame_count} sampled frames produced {len(chunk.observations)} observations.",
    ]

    if "multiple_person_presence" in chunk.events:
        sentences.append("Multiple faces were visible inside the same chunk.")
    if "candidate_absence" in chunk.events:
        sentences.append("The candidate disappeared from view for a sustained span.")
    if "attention_deviation" in chunk.events:
        sentences.append("Face placement drifted away from the frame center repeatedly.")
    if "suspicious_object_activity" in chunk.events:
        sentences.append("Desk-area motion stayed elevated and may warrant review for a phone or notes.")

    return " ".join(sentences)


def _make_risk_label(score: float) -> str:
    if score >= 0.7:
        return "high"
    if score >= 0.4:
        return "medium"
    return "low"


def _chunk_events(
    face_peak: int,
    no_face_ratio: float,
    attention_score: float,
    motion_score: float,
    absence_threshold: float,
    attention_threshold: float,
    motion_threshold: float,
) -> List[str]:
    events: List[str] = []
    if face_peak > 1:
        events.append("multiple_person_presence")
    if no_face_ratio >= absence_threshold:
        events.append("candidate_absence")
    if attention_score >= attention_threshold and face_peak >= 1:
        events.append("attention_deviation")
    if motion_score >= motion_threshold:
        events.append("suspicious_object_activity")
    return events


def _weighted_risk(
    face_peak: int,
    no_face_ratio: float,
    attention_score: float,
    motion_score: float,
) -> float:
    multiple_score = min(1.0, face_peak / 2.0)
    absence_score = min(1.0, no_face_ratio)
    attention_component = min(1.0, attention_score)
    motion_component = min(1.0, motion_score * 3.0)
    total = (
        0.35 * multiple_score
        + 0.30 * absence_score
        + 0.20 * attention_component
        + 0.15 * motion_component
    )
    return float(max(0.0, min(1.0, total)))


def _build_observations(
    sample_count: int,
    face_samples: int,
    face_peak: int,
    no_face_ratio: float,
    attention_score: float,
    motion_score: float,
) -> List[str]:
    observations = [
        f"{face_samples} of {sample_count} sampled frames contained a visible face.",
        f"Peak face count in the chunk was {face_peak}.",
        f"No-face ratio was {no_face_ratio:.0%}.",
        f"Average motion score was {motion_score:.2f}.",
    ]
    if face_samples:
        observations.append(f"Average frame-centre deviation was {attention_score:.2f}.")
    return observations


def _finalize_chunk(chunk_id: int, chunk_seconds: int, duration_seconds: float, stats: Dict[str, float], ocr_text: str = "") -> EvidenceChunk:
    sample_count = max(1, int(stats["sample_count"]))
    face_samples = int(stats["face_samples"])
    face_peak = int(stats["face_peak"])
    no_face_ratio = float(stats["no_face_count"] / sample_count)
    attention_score = float(stats["attention_sum"] / max(1, face_samples))
    motion_score = float(stats["motion_sum"] / sample_count)
    
    start_time = chunk_id * chunk_seconds
    end_time = min(duration_seconds, start_time + chunk_seconds)

    # Generate a raw textual description of the frame based on OpenCV signals + OCR
    raw_desc = []
    if face_peak > 1:
        raw_desc.append("Multiple faces or persons are present in the camera frame.")
    elif no_face_ratio > float(stats.get("absence_threshold", 0.5)):
        raw_desc.append("The candidate is absent from the camera view.")
    elif attention_score > float(stats.get("attention_threshold", 0.35)):
        raw_desc.append("The candidate repeatedly looks away or deviates attention from the screen.")
    elif motion_score > float(stats.get("motion_threshold", 0.12)):
        raw_desc.append("Suspicious object or hand activity with high motion. A mobile phone, handheld device, or phone-like object might be visible.")
    else:
        raw_desc.append("The candidate is visible with stable behaviour and low-risk signals.")
    
    if ocr_text:
        raw_desc.append(f"Text detected on screen mentions: {ocr_text}")
        if "phone" in ocr_text.lower() or "mobile" in ocr_text.lower():
            raw_desc.append("A mobile phone, handheld device, or phone-like object is mentioned in text.")

    frame_description = " ".join(raw_desc)

    # Reference Matching
    events = []
    risk_score = 0.0
    matched_pattern = "normal"
    if REFERENCE_MATRIX is not None:
        frame_vec = REFERENCE_VECTORIZER.transform([frame_description])
        sims = cosine_similarity(frame_vec, REFERENCE_MATRIX).ravel()
        best_idx = int(np.argmax(sims))
        best_score = float(sims[best_idx])
        matched_pattern = REFERENCE_LABELS[best_idx]
        
        if matched_pattern != "normal" and best_score > 0.1:
            events.append(matched_pattern)
            risk_score = min(1.0, best_score + 0.3)
        else:
            risk_score = 0.1
    
    observations = _build_observations(sample_count, face_samples, face_peak, no_face_ratio, attention_score, motion_score)
    observations.append(f"Matched Reference Pattern: '{REFERENCE_PATTERNS.get(matched_pattern, matched_pattern)}'")

    description = f"{format_timecode(start_time)} to {format_timecode(end_time)}: {frame_description}"

    return EvidenceChunk(
        chunk_id=chunk_id,
        start_time=start_time,
        end_time=end_time,
        frame_count=int(stats.get("frame_count", 0)),
        sample_count=sample_count,
        face_peak=face_peak,
        no_face_ratio=no_face_ratio,
        motion_score=motion_score,
        attention_score=attention_score,
        risk_score=risk_score,
        risk_label=_make_risk_label(risk_score),
        events=events,
        observations=observations,
        description=description,
        keyframe_note=f"Representative moment from {format_timecode(start_time)} to {format_timecode(end_time)}",
    )


def analyze_video_bytes(
    video_bytes: bytes,
    video_name: str,
    chunk_seconds: int,
    sample_rate: float,
    absence_threshold: float,
    attention_threshold: float,
    motion_threshold: float,
) -> AnalysisReport:
    suffix = os.path.splitext(video_name)[1] or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(video_bytes)
        temp_path = temp_file.name

    capture = cv2.VideoCapture(temp_path)
    try:
        if not capture.isOpened():
            raise RuntimeError("The uploaded file could not be opened as a video.")

        fps = float(capture.get(cv2.CAP_PROP_FPS) or 25.0)
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        duration_seconds = frame_count / fps if frame_count > 0 and fps > 0 else 0.0
        sample_step = max(1, int(round(fps / max(0.1, sample_rate))))
        face_detector = _safe_face_detector()

        chunk_stats: Dict[int, Dict[str, float]] = defaultdict(
            lambda: {
                "frame_count": 0,
                "sample_count": 0,
                "face_samples": 0,
                "face_peak": 0,
                "no_face_count": 0,
                "motion_sum": 0.0,
                "attention_sum": 0.0,
                "absence_threshold": absence_threshold,
                "attention_threshold": attention_threshold,
                "motion_threshold": motion_threshold,
            }
        )

        previous_gray: np.ndarray | None = None
        frame_index = 0
        while True:
            ok, frame = capture.read()
            if not ok:
                break

            current_chunk = int((frame_index / fps) // chunk_seconds) if fps > 0 else 0
            chunk_stats[current_chunk]["frame_count"] += 1

            if frame_index % sample_step != 0:
                frame_index += 1
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Make face detection much stricter to avoid false positives (like phones being detected as faces)
            faces = face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=12, minSize=(60, 60))
            face_count = len(faces)

            motion_score = 0.0
            if previous_gray is not None:
                resized_previous = cv2.resize(previous_gray, (160, 90))
                resized_current = cv2.resize(gray, (160, 90))
                motion_score = float(np.mean(cv2.absdiff(resized_previous, resized_current)) / 255.0)

            attention_score = 0.0
            if face_count:
                x, y, width, height = max(faces, key=lambda box: box[2] * box[3])
                face_centre_x = x + (width / 2.0)
                face_centre_y = y + (height / 2.0)
                frame_centre_x = frame.shape[1] / 2.0
                frame_centre_y = frame.shape[0] / 2.0
                max_distance = math.hypot(frame_centre_x, frame_centre_y)
                attention_score = float(
                    min(1.0, math.hypot(face_centre_x - frame_centre_x, face_centre_y - frame_centre_y) / max_distance)
                )

            stats = chunk_stats[current_chunk]
            stats["sample_count"] += 1
            stats["face_samples"] += int(face_count > 0)
            stats["face_peak"] = max(stats["face_peak"], face_count)
            stats["no_face_count"] += int(face_count == 0)
            stats["motion_sum"] += motion_score
            stats["attention_sum"] += attention_score
            
            # Store the last frame of the chunk for OCR extraction
            stats["last_frame"] = frame
            
            previous_gray = gray
            frame_index += 1

        chunks = []
        for chunk_id, stats in sorted(chunk_stats.items(), key=lambda item: item[0]):
            ocr_text = ""
            if "last_frame" in stats and pytesseract is not None:
                try:
                    rgb_frame = cv2.cvtColor(stats["last_frame"], cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(rgb_frame)
                    extracted = pytesseract.image_to_string(pil_img)
                    if extracted and extracted.strip():
                        ocr_text = " ".join(extracted.strip().split())
                except:
                    pass
            chunks.append(_finalize_chunk(chunk_id, chunk_seconds, duration_seconds, stats, ocr_text))
        summary = _build_summary(chunks, video_name)
        return AnalysisReport(
            video_name=video_name,
            source="uploaded video",
            duration_seconds=duration_seconds,
            fps=fps,
            chunk_seconds=chunk_seconds,
            sample_rate=sample_rate,
            chunks=chunks,
            summary=summary,
        )
    finally:
        capture.release()
        try:
            os.remove(temp_path)
        except OSError:
            pass


def _build_summary(chunks: Sequence[EvidenceChunk], video_name: str) -> str:
    suspicious = sum(1 for chunk in chunks if chunk.risk_label != "low")
    high_risk = sum(1 for chunk in chunks if chunk.risk_label == "high")
    return (
        f"{video_name} was broken into {len(chunks)} temporal evidence chunks. "
        f"The analysis surfaced {suspicious} chunks above low risk, including {high_risk} high-risk segments. "
        f"The report should be used to guide human review, not to automatically declare malpractice."
    )


def build_vector_store(chunks: Sequence[EvidenceChunk]) -> VectorStore:
    corpus = [f"{chunk.description} {' '.join(chunk.events)} {' '.join(chunk.observations)}" for chunk in chunks]
    if not corpus:
        corpus = ["empty evidence corpus"]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
    matrix = vectorizer.fit_transform(corpus)
    return VectorStore(chunks=list(chunks), vectorizer=vectorizer, matrix=matrix)


def retrieve_chunks(vector_store: VectorStore, query: str, top_k: int) -> List[Tuple[EvidenceChunk, float]]:
    if not vector_store.chunks:
        return []
    query_text = (query or "suspicious examination evidence").strip()
    query_vector = vector_store.vectorizer.transform([query_text])
    similarity_scores = cosine_similarity(query_vector, vector_store.matrix).ravel()
    ranked_indices = np.argsort(similarity_scores)[::-1][:top_k]
    results: List[Tuple[EvidenceChunk, float]] = []
    for index in ranked_indices:
        results.append((vector_store.chunks[int(index)], float(similarity_scores[int(index)])))
    return results


def rerank_hits(query: str, retrieved: Sequence[Tuple[EvidenceChunk, float]], top_n: int) -> List[RetrievalHit]:
    query_lower = query.lower()
    ranked: List[RetrievalHit] = []
    for chunk, similarity in retrieved:
        keyword_bonus = 0.0
        reasons: List[str] = []
        for keyword, mapped_events in QUERY_HINTS.items():
            if keyword in query_lower and any(event in chunk.events for event in mapped_events):
                keyword_bonus += 0.15
                label_text = ", ".join(EVENT_LABELS[event] for event in mapped_events)
                reasons.append(f"Query term '{keyword}' reinforced {label_text}.")

        risk_bonus = min(0.25, chunk.risk_score * 0.25)
        rerank_score = min(1.0, 0.7 * similarity + risk_bonus + keyword_bonus)
        if not reasons:
            reasons.append("Semantic similarity matched the evidence description and observation text.")
        ranked.append(
            RetrievalHit(
                chunk=chunk,
                similarity=float(similarity),
                rerank_score=float(rerank_score),
                match_reason=" ".join(reasons),
            )
        )
    ranked.sort(key=lambda hit: hit.rerank_score, reverse=True)
    return ranked[:top_n]


def _call_ollama(prompt: str, endpoint: str, model: str) -> str | None:
    url = endpoint.rstrip("/") + "/api/generate"
    try:
        response = requests.post(
            url,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=45,
        )
        response.raise_for_status()
        payload = response.json()
        text = str(payload.get("response", "")).strip()
        return text or None
    except Exception:
        return None


def _build_prompt(query: str, hits: Sequence[RetrievalHit]) -> str:
    lines = [
        "You are assisting a human examiner reviewing recorded exam evidence.",
        "Do not accuse the candidate of cheating. Only identify potentially suspicious activity.",
        f"Investigation query: {query}",
        "Evidence:",
    ]
    for index, hit in enumerate(hits, start=1):
        chunk = hit.chunk
        lines.append(
            f"{index}. {format_timecode(chunk.start_time)}-{format_timecode(chunk.end_time)} | "
            f"risk={chunk.risk_label} ({hit.rerank_score:.2f}) | {chunk.description}"
        )
    lines.append(
        "Return a concise structured response with event, timestamp, evidence, risk level, confidence, and recommendation."
    )
    return "\n".join(lines)


def synthesize_review(
    query: str,
    hits: Sequence[RetrievalHit],
    use_ollama: bool,
    ollama_url: str,
    ollama_model: str,
) -> Dict[str, object]:
    prompt = _build_prompt(query, hits)
    llm_response = _call_ollama(prompt, ollama_url, ollama_model) if use_ollama else None
    if llm_response:
        provider = "ollama"
        narrative = llm_response
    else:
        provider = "rule-based fallback"
        narrative = _fallback_summary(query, hits)

    findings = []
    for hit in hits:
        chunk = hit.chunk
        event_names = [EVENT_LABELS.get(event, event) for event in chunk.events] or ["low-risk observation"]
        confidence = round(max(0.35, min(0.99, hit.rerank_score)), 2)
        findings.append(
            {
                "event": "; ".join(event_names),
                "timestamp": f"{format_timecode(chunk.start_time)} - {format_timecode(chunk.end_time)}",
                "evidence": chunk.observations[:3],
                "risk": chunk.risk_label.upper(),
                "confidence": confidence,
                "recommendation": "REVIEW_REQUIRED" if chunk.risk_label != "low" else "MONITOR",
            }
        )

    return {
        "provider": provider,
        "prompt": prompt,
        "narrative": narrative,
        "findings": findings,
    }


def _fallback_summary(query: str, hits: Sequence[RetrievalHit]) -> str:
    if not hits:
        return "No evidence chunks matched the investigation query."
    lead = hits[0].chunk
    lines = [
        f"Investigation query: {query}",
        f"Top evidence: {lead.description}",
        "Recommended action: review the highlighted timestamps in the original video before drawing any conclusion.",
    ]
    for hit in hits[:3]:
        chunk = hit.chunk
        lines.append(
            f"- {format_timecode(chunk.start_time)}-{format_timecode(chunk.end_time)}: "
            f"{chunk.risk_label.upper()} risk, rerank score {hit.rerank_score:.2f}."
        )
    return "\n".join(lines)


def build_demo_bundle() -> Tuple[AnalysisReport, VectorStore]:
    chunks = [
        EvidenceChunk(
            chunk_id=0,
            start_time=0,
            end_time=10,
            frame_count=240,
            sample_count=10,
            face_peak=1,
            no_face_ratio=0.0,
            motion_score=0.08,
            attention_score=0.12,
            risk_score=0.12,
            risk_label="low",
            events=[],
            observations=[
                "One candidate stayed visible for the full interval.",
                "Motion levels remained steady.",
                "No obvious secondary person was detected.",
            ],
            description="Candidate remained visible and stable, with no strong malpractice indicators.",
            keyframe_note="Representative start-of-exam frame.",
        ),
        EvidenceChunk(
            chunk_id=1,
            start_time=10,
            end_time=20,
            frame_count=240,
            sample_count=10,
            face_peak=2,
            no_face_ratio=0.0,
            motion_score=0.15,
            attention_score=0.22,
            risk_score=0.81,
            risk_label="high",
            events=["multiple_person_presence"],
            observations=[
                "Two faces were visible in several sampled moments.",
                "The second face entered the frame from the side.",
                "Review is required to confirm whether another person was present.",
            ],
            description="Multiple faces appeared in the same chunk, suggesting possible second-person presence.",
            keyframe_note="Side-entry face pattern captured in the middle of the chunk.",
        ),
        EvidenceChunk(
            chunk_id=2,
            start_time=20,
            end_time=30,
            frame_count=240,
            sample_count=10,
            face_peak=1,
            no_face_ratio=0.0,
            motion_score=0.27,
            attention_score=0.48,
            risk_score=0.72,
            risk_label="high",
            events=["attention_deviation", "suspicious_object_activity"],
            observations=[
                "The face drifted away from the frame centre repeatedly.",
                "Desk-area motion increased across the chunk.",
                "This pattern is consistent with a review of possible notes or a phone-like object.",
            ],
            description="Repeated off-centre face placement and elevated desk motion could indicate suspicious object handling.",
            keyframe_note="Mid-exam chunk with repeated motion spikes.",
        ),
        EvidenceChunk(
            chunk_id=3,
            start_time=30,
            end_time=40,
            frame_count=240,
            sample_count=10,
            face_peak=0,
            no_face_ratio=1.0,
            motion_score=0.03,
            attention_score=0.0,
            risk_score=0.79,
            risk_label="high",
            events=["candidate_absence"],
            observations=[
                "No face was detected in the sampled frames.",
                "The candidate was out of view for the entire interval.",
                "The segment should be reviewed for an absence explanation.",
            ],
            description="Candidate absence persisted throughout the chunk and should be reviewed.",
            keyframe_note="Empty chair segment.",
        ),
        EvidenceChunk(
            chunk_id=4,
            start_time=40,
            end_time=50,
            frame_count=240,
            sample_count=10,
            face_peak=1,
            no_face_ratio=0.0,
            motion_score=0.19,
            attention_score=0.36,
            risk_score=0.59,
            risk_label="medium",
            events=["suspicious_object_activity"],
            observations=[
                "Motion on the desk increased during the chunk.",
                "The subject briefly lowered their gaze several times.",
                "This may warrant a quick human review for a phone or notes.",
            ],
            description="Elevated desk activity suggests a possible phone-like object or note handling.",
            keyframe_note="Desk-motion segment.",
        ),
    ]
    report = AnalysisReport(
        video_name="demo_exam_video.mp4",
        source="demo dataset",
        duration_seconds=50.0,
        fps=24.0,
        chunk_seconds=10,
        sample_rate=1.0,
        chunks=chunks,
        summary=(
            "Demo evidence contains multiple review-worthy segments that demonstrate how the retrieval and "
            "reranking pipeline prioritises suspicious examination activity."
        ),
    )
    return report, build_vector_store(chunks)


def report_to_json(report: AnalysisReport, vector_store: VectorStore | None = None, investigation: Dict[str, object] | None = None) -> str:
    payload = asdict(report)
    if vector_store is not None:
        payload["vector_store_chunk_count"] = len(vector_store.chunks)
    if investigation is not None:
        payload["investigation"] = investigation
    return json.dumps(payload, indent=2)


def build_timeline_frame(report: AnalysisReport) -> pd.DataFrame:
    rows = []
    for chunk in report.chunks:
        rows.append(
            {
                "chunk_id": chunk.chunk_id,
                "start": format_timecode(chunk.start_time),
                "end": format_timecode(chunk.end_time),
                "risk_score": round(chunk.risk_score, 2),
                "risk_label": chunk.risk_label,
                "events": ", ".join(chunk.events) if chunk.events else "none",
            }
        )
    return pd.DataFrame(rows)
