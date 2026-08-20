"""
agent/nodes/student_lookup.py
--------------------------------
Third agent node: matches the detected face embedding against the student
database (pgvector nearest-neighbour search) to identify who is in frame,
and fetches their profile details.
"""
from __future__ import annotations

import logging

from agent.state import RiskScoringState
from database.connection import session_scope
from database.repository import find_closest_student_by_embedding, get_student_by_code
from risk_scoring.rules import FACE_MATCH_DISTANCE_THRESHOLD

logger = logging.getLogger(__name__)


def run(state: RiskScoringState) -> RiskScoringState:
    embedding = state.get("primary_embedding")
    claimed_code = state.get("claimed_student_code")

    state["matched_student_id"] = None
    state["matched_student_name"] = None
    state["matched_student_code"] = None
    state["face_match_distance"] = None

    with session_scope() as db:
        # If admin/proctor selected a specific student, ALWAYS target that student
        if claimed_code:
            student = get_student_by_code(db, claimed_code)
            if student:
                state["matched_student_id"] = student.id
                state["matched_student_name"] = student.full_name
                state["matched_student_code"] = student.roll_number or student.student_code
                state["matched_student_profile_image"] = student.passport_image_path or student.profile_image_path or student.id_card_image_path
                
                # Check face match against THIS claimed student's registered embedding
                if embedding is not None and student.face_embedding:
                    import numpy as np
                    reg_emb = np.array(student.face_embedding, dtype=np.float64)
                    cur_emb = np.array(embedding, dtype=np.float64)
                    distance = float(np.linalg.norm(reg_emb - cur_emb))
                    state["face_match_distance"] = distance
                    logger.info(
                        "[student_lookup] verified against claimed student %s (%s): distance=%.3f",
                        student.full_name, student.student_code, distance,
                    )
                elif embedding is not None:
                    # Student has no registered embedding
                    state["face_match_distance"] = 0.30
                return state

        # Fallback: if no claimed code was passed, search DB by closest embedding
        if embedding is not None:
            matches = find_closest_student_by_embedding(db, embedding, top_k=1)
            if matches:
                student, distance = matches[0]
                state["matched_student_id"] = student.id
                state["matched_student_name"] = student.full_name
                state["matched_student_code"] = student.roll_number or student.student_code
                state["face_match_distance"] = float(distance)
                logger.info(
                    "[student_lookup] closest match: %s (distance=%.3f, threshold=%.3f)",
                    student.student_code, distance, FACE_MATCH_DISTANCE_THRESHOLD,
                )
                return state

    return state

