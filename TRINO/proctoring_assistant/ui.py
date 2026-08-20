from __future__ import annotations

import hashlib
from typing import Tuple

import streamlit as st

from .config import DATABASE_URL, OLLAMA_MODEL, OLLAMA_URL, VECTOR_DB_PATH
from .service import EvidenceService
from utils.pipeline import (
    AnalysisReport,
    VectorStore,
    analyze_video_bytes,
    build_demo_bundle,
    build_timeline_frame,
    build_vector_store,
    report_to_json,
    retrieve_chunks,
    rerank_hits,
    synthesize_review,
)


def _analysis_bundle_from_upload(
    video_bytes: bytes,
    video_name: str,
    chunk_seconds: int,
    sample_rate: float,
    absence_threshold: float,
    attention_threshold: float,
    motion_threshold: float,
) -> Tuple[AnalysisReport, VectorStore]:
    report = analyze_video_bytes(
        video_bytes=video_bytes,
        video_name=video_name,
        chunk_seconds=chunk_seconds,
        sample_rate=sample_rate,
        absence_threshold=absence_threshold,
        attention_threshold=attention_threshold,
        motion_threshold=motion_threshold,
    )
    return report, build_vector_store(report.chunks)


@st.cache_data(show_spinner=False)
def cached_upload_bundle(
    video_bytes: bytes,
    video_name: str,
    chunk_seconds: int,
    sample_rate: float,
    absence_threshold: float,
    attention_threshold: float,
    motion_threshold: float,
) -> Tuple[AnalysisReport, VectorStore]:
    return _analysis_bundle_from_upload(
        video_bytes,
        video_name,
        chunk_seconds,
        sample_rate,
        absence_threshold,
        attention_threshold,
        motion_threshold,
    )


@st.cache_data(show_spinner=False)
def cached_demo_bundle() -> Tuple[AnalysisReport, VectorStore]:
    return build_demo_bundle()


@st.cache_resource(show_spinner=False)
def cached_evidence_service() -> EvidenceService:
    service = EvidenceService(
        database_url=DATABASE_URL,
        vector_path=VECTOR_DB_PATH,
    )
    service.ensure_demo_data()
    return service


def main() -> None:
    st.set_page_config(
        page_title="Offline RAG proctoring",
        page_icon=":material/query_stats:",
        layout="wide",
    )

    if "bundle" not in st.session_state:
        st.session_state.bundle = cached_demo_bundle()
    if "investigation" not in st.session_state:
        st.session_state.investigation = None
    if "last_upload_hash" not in st.session_state:
        st.session_state.last_upload_hash = ""
    if "agent_investigation" not in st.session_state:
        st.session_state.agent_investigation = None

    st.title("AI Exam Proctoring Assistant")
    st.caption("Evidence-first exam review built for human investigators.")

    with st.sidebar:
        st.header("Analysis settings")
        chunk_seconds = st.slider("Chunk length (seconds)", min_value=5, max_value=60, value=10, step=5)
        sample_rate = st.slider("Samples per second", min_value=1, max_value=6, value=2, step=1)
        absence_threshold = st.slider("Absence threshold", min_value=0.30, max_value=0.90, value=0.55, step=0.05)
        attention_threshold = st.slider("Attention threshold", min_value=0.10, max_value=0.80, value=0.35, step=0.05)
        motion_threshold = st.slider("Motion threshold", min_value=0.05, max_value=0.40, value=0.12, step=0.01)
        top_k = st.slider("Top-k retrieval", min_value=3, max_value=12, value=8, step=1)
        rerank_top_n = st.slider("Rerank top-n", min_value=2, max_value=6, value=4, step=1)
        use_ollama = st.checkbox("Use local Ollama when available", value=False)
        ollama_url = st.text_input("Ollama URL", value="http://localhost:11434")
        ollama_model = st.text_input("Ollama model", value="llama3.1")

    upload_col, demo_col = st.columns(2)
    with upload_col:
        uploaded_video = st.file_uploader("Upload recorded exam video", type=["mp4", "mov", "avi", "mkv"])
    with demo_col:
        load_demo = st.button("Load demo evidence")

    if load_demo:
        st.session_state.bundle = cached_demo_bundle()
        st.session_state.investigation = None

    if uploaded_video is not None:
        upload_hash = hashlib.sha256(uploaded_video.getvalue()).hexdigest()
        if upload_hash != st.session_state.last_upload_hash:
            with st.spinner("Analyzing uploaded video and building evidence index..."):
                st.session_state.bundle = cached_upload_bundle(
                    uploaded_video.getvalue(),
                    uploaded_video.name,
                    chunk_seconds,
                    float(sample_rate),
                    float(absence_threshold),
                    float(attention_threshold),
                    float(motion_threshold),
                )
            st.session_state.last_upload_hash = upload_hash
            st.session_state.investigation = None

    report, vector_store = st.session_state.bundle
    evidence_service = cached_evidence_service()
    report_key = f"{report.video_name}:{report.duration_seconds}:{len(report.chunks)}"
    if st.session_state.get("indexed_report_key") != report_key:
        evidence_service.ingest_video_report(report)
        st.session_state.indexed_report_key = report_key

    metric_a, metric_b, metric_c, metric_d = st.columns(4)
    chunk_count = len(report.chunks)
    suspicious_count = sum(1 for chunk in report.chunks if chunk.risk_label != "low")
    high_count = sum(1 for chunk in report.chunks if chunk.risk_label == "high")
    top_risk = max((chunk.risk_score for chunk in report.chunks), default=0.0)
    metric_a.metric("Chunks analyzed", f"{chunk_count}")
    metric_b.metric("Suspicious chunks", f"{suspicious_count}")
    metric_c.metric("High-risk chunks", f"{high_count}")
    metric_d.metric("Peak risk score", f"{top_risk:.2f}")

    overview_tab, investigation_tab, method_tab = st.tabs(["Evidence timeline", "Investigation", "Method"])

    with overview_tab:
        left, right = st.columns([1.3, 1])
        with left:
            st.subheader("Evidence timeline")
            timeline_df = build_timeline_frame(report)
            if not timeline_df.empty:
                chart_df = timeline_df.copy()
                chart_df["chunk_start_seconds"] = [chunk.start_time for chunk in report.chunks]
                st.line_chart(chart_df.set_index("chunk_start_seconds")["risk_score"])
                st.dataframe(timeline_df)
            else:
                st.info("No evidence chunks are available yet.")
        with right:
            st.subheader("System summary")
            st.write(report.summary)
            st.caption(
                f"Source: {report.source} | Duration: {report.duration_seconds:.1f}s | FPS: {report.fps:.1f} | Chunk size: {report.chunk_seconds}s"
            )
            st.download_button(
                label="Download report JSON",
                data=report_to_json(report, vector_store),
                file_name="exam_proctoring_report.json",
                mime="application/json",
            )

        st.subheader("Flagged chunks")
        flagged_chunks = sorted(report.chunks, key=lambda chunk: chunk.risk_score, reverse=True)
        for chunk in flagged_chunks:
            with st.expander(
                f"{chunk.risk_label.upper()} risk | {chunk.start_time:0.0f}s - {chunk.end_time:0.0f}s | score {chunk.risk_score:.2f}",
                expanded=chunk.risk_label == "high",
            ):
                st.write(chunk.description)
                st.write("Observations:")
                for observation in chunk.observations:
                    st.markdown(f"- {observation}")
                if chunk.events:
                    st.markdown(f"**Events:** {', '.join(chunk.events)}")
                else:
                    st.markdown("**Events:** none")
                st.caption(chunk.keyframe_note)

    with investigation_tab:
        st.subheader("Agentic investigation")
        agent_query = st.text_input(
            "Evidence investigation query",
            value="Find phone-related suspicious evidence for STU102",
            key="agent_query",
        )
        run_agent_query = st.button("Run agentic investigation", type="primary")
        if run_agent_query:
            with st.spinner("Routing query and retrieving evidence..."):
                st.session_state.agent_investigation = evidence_service.investigate(
                    agent_query,
                    top_k=top_k,
                    use_ollama=use_ollama,
                    ollama_url=ollama_url or OLLAMA_URL,
                    ollama_model=ollama_model or OLLAMA_MODEL,
                )

        agent_investigation = st.session_state.agent_investigation
        if agent_investigation is not None:
            st.info(f"Search strategy: {agent_investigation['query_type']}")
            st.markdown(agent_investigation["final_answer"])
            st.caption(
                "Evidence references: "
                + (", ".join(agent_investigation["evidence_references"]) or "none")
            )
            with st.expander("Agent retrieval and reranking details"):
                st.json(agent_investigation["reranked_documents"])

        st.subheader("Retrieval and reranking")
        preset_queries = [
            "Find evidence related to mobile phone usage.",
            "Find segments where multiple people may be present.",
            "Find candidate absence or missing camera coverage.",
            "Find suspicious exam behaviour.",
        ]
        preset_query = st.selectbox("Investigation query preset", options=preset_queries)
        query = st.text_input("Investigation query", value=preset_query)
        run_query = st.button("Run retrieval")

        if run_query:
            retrieved = retrieve_chunks(vector_store, query, top_k=top_k)
            reranked = rerank_hits(query, retrieved, top_n=rerank_top_n)
            summary = synthesize_review(query, reranked, use_ollama, ollama_url, ollama_model)
            st.session_state.investigation = {
                "query": query,
                "retrieved": retrieved,
                "reranked": reranked,
                "summary": summary,
            }

        if st.session_state.investigation is None:
            st.info("Run retrieval to produce a ranked evidence answer for the selected query.")
        else:
            investigation = st.session_state.investigation
            reranked = investigation["reranked"]
            summary = investigation["summary"]
            st.markdown("### Structured review output")
            st.write(summary["narrative"])
            st.caption(f"Reasoning provider: {summary['provider']}")

            with st.expander("Model prompt and structured findings"):
                st.text(summary["prompt"])
                st.json(summary["findings"])

            st.markdown("### Ranked evidence")
            for hit in reranked:
                chunk = hit.chunk
                with st.container():
                    st.markdown(
                        f"**{chunk.risk_label.upper()}** | {chunk.start_time:0.0f}s - {chunk.end_time:0.0f}s | "
                        f"similarity {hit.similarity:.2f} | rerank {hit.rerank_score:.2f}"
                    )
                    st.write(chunk.description)
                    st.caption(hit.match_reason)
                    st.markdown(f"**Evidence:** {'; '.join(chunk.observations[:2])}")

    with method_tab:
        st.subheader("How the prototype works")
        st.markdown(
            """
            1. The uploaded exam video is sampled into temporal chunks.
            2. A frame from each chunk is extracted and processed using OpenCV heuristics and OCR.
            3. A raw textual description of the frame is generated from these signals.
            4. The frame's description is embedded and matched against a **Reference Database** of known suspicious behaviors using cosine similarity (Few-Shot Visual Reference Matching).
            5. If a high similarity match is found, the chunk is flagged with the reference pattern's risk score.
            6. The top evidence is passed to a local Ollama model when available, or to a deterministic fallback summary.
            7. The final output stays human-review-first.
            """
        )


if __name__ == "__main__":
    main()
