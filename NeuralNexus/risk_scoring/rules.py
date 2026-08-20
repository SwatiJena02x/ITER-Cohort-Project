"""
risk_scoring/rules.py
------------------------
Deterministic risk weights and severity rules. All numbers live here so the
scoring logic in scorer.py stays simple and these thresholds can be tuned
(e.g. by an academic-integrity committee) without touching code elsewhere.
"""

# Base points added to the risk score per malpractice type detected,
# scaled by the detector's confidence (points * confidence).
MALPRACTICE_BASE_WEIGHTS: dict[str, float] = {
    "phone_usage": 40.0,
    "bluetooth_earbud": 45.0,
    "phone_call_posture": 40.0,
    "unauthorized_material": 25.0,
    "unauthorized_device": 30.0,
    "multiple_people": 35.0,
    "impersonation": 50.0,        # face doesn't match registered profile
    "no_face_detected": 20.0,     # student not visible in frame
    "eye_movement_away": 20.0,    # student looking away from screen
    "talking_detected": 25.0,     # student talking during examination
}

# Extra flat points added for identity issues (independent of object detection).
FACE_MATCH_PENALTY = 30.0       # face detected but doesn't match registered student
NO_FACE_PENALTY = 20.0          # no face detected at all in the frame
MULTIPLE_FACES_PENALTY = 25.0   # more than one face detected

# Score is clamped to [0, 100].
MIN_SCORE = 0.0
MAX_SCORE = 100.0

# Risk level thresholds (inclusive lower bound).
RISK_LEVEL_THRESHOLDS: list[tuple[float, str]] = [
    (0.0, "LOW"),
    (35.0, "MEDIUM"),
    (65.0, "HIGH"),
    (85.0, "CRITICAL"),
]

# Face match: cosine/L2 distance below this = same person (tune per embedding model).
FACE_MATCH_DISTANCE_THRESHOLD = 0.55


def classify_risk_level(score: float) -> str:
    """Map a numeric score (0-100) to a categorical risk level."""
    level = "LOW"
    for threshold, name in RISK_LEVEL_THRESHOLDS:
        if score >= threshold:
            level = name
        else:
            break
    return level
