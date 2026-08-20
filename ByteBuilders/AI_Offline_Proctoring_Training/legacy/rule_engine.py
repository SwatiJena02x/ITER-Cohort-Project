"""Standalone regex-based evidence classifier.

NOTE: this file is not imported anywhere in graph/workflow.py -- the
active pipeline scores evidence via agents/risk_agent.py and explains it
via agents/synthesis_agent.py (FAISS + embedded rules + LLM). This module
predates that and was self-contained (no rules.txt / config dependency)
even before the rules.txt removal elsewhere in this project. Kept here in
case you're using it separately; safe to delete if not.
"""

import re

# Self-contained: no external rules.txt / config file dependency.
SUSPICIOUS_OBJECTS = (
    "cell phone",
    "phone",
    "book",
    "laptop",
    "tablet",
    "remote",
    "tv",
    "keyboard",
    "mouse",
)

# One combined pattern instead of re-scanning each item once per object.
# Captures which object matched plus its confidence score.
_OBJECT_SCORE_PATTERN = re.compile(
    r"(" + "|".join(re.escape(obj) for obj in SUSPICIOUS_OBJECTS) + r")"
    r"\s*\((0\.\d+|1\.0+)\)"
)

HIGH_CONFIDENCE_THRESHOLD = 0.80
LOW_CONFIDENCE_THRESHOLD = 0.50


def analyze_evidence(evidence):
    """Classify evidence strings by the highest-confidence suspicious-object match.

    Each evidence string is scanned once for any "<object> (<score>)" pattern
    (e.g. "cell phone (0.92)"). Items are bucketed by their highest matching
    confidence score:
        >= 0.80  -> strong_evidence
        >= 0.50  -> weak_evidence
        else     -> ignored

    Args:
        evidence: Iterable of evidence strings.

    Returns:
        Tuple of (status, severity, strong_evidence, weak_evidence) where:
            status: "FLAG FOR REVIEW" or "CLEAR"
            severity: "HIGH" or "MEDIUM"
            strong_evidence: list of items with a match >= 0.80 (order preserved, deduped)
            weak_evidence: list of items with a match >= 0.50 and < 0.80 (order preserved, deduped)
    """
    strong_evidence = []
    weak_evidence = []
    seen_strong = set()
    seen_weak = set()

    for item in evidence:
        text = item.lower()

        matches = _OBJECT_SCORE_PATTERN.findall(text)
        if not matches:
            continue

        # Use the highest confidence score found in this item to classify it.
        best_score = max(float(score) for _, score in matches)

        if best_score >= HIGH_CONFIDENCE_THRESHOLD:
            if item not in seen_strong:
                seen_strong.add(item)
                strong_evidence.append(item)
        elif best_score >= LOW_CONFIDENCE_THRESHOLD:
            if item not in seen_weak:
                seen_weak.add(item)
                weak_evidence.append(item)

    if strong_evidence:
        return ("FLAG FOR REVIEW", "HIGH", strong_evidence, weak_evidence)

    if weak_evidence:
        return ("FLAG FOR REVIEW", "MEDIUM", strong_evidence, weak_evidence)

    return ("CLEAR", "MEDIUM", strong_evidence, weak_evidence)
