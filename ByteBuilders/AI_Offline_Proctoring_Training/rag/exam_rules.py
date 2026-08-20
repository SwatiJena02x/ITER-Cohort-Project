"""Embedded examination rules used by the risk synthesis pipeline.

Belongs in the `rag` package (rag/exam_rules.py).

Previously synthesis_agent.py read data/rules/rules.txt from disk on every
process start (and re-checked its mtime on every single node call). That
coupled the pipeline to a piece of deployment-time filesystem state: the
file had to exist, in the right place, with the right encoding, before the
graph could even run a LOW-risk session, and a typo'd path failed silently
into an empty rule set.

Rules now live here as a versioned Python constant instead. Same
LLM-usable rule text, same chunk-embed-index flow in synthesis_agent.py --
but it ships with the codebase, gets reviewed in PRs like any other logic
change, and has zero filesystem dependency. Edit EXAM_RULES_TEXT directly
to add, remove, or reword rules; no external file, no redeploy step beyond
a normal code change.
"""

EXAM_RULES_TEXT = """\
RULE 1: Mobile phones, smartwatches, and any other electronic communication
devices are strictly prohibited in the examination area for the duration
of the exam, whether powered on or off.

RULE 2: Candidates may not access books, printed notes, or written
material of any kind unless the exam has been explicitly designated
"open-book" by the instructor.

RULE 3: Only one person -- the enrolled candidate -- may be present at the
exam location. The presence of any additional person in the camera's
field of view is a violation, regardless of whether that person is
observed assisting the candidate.

RULE 4: Candidates may not communicate with any other person, in person
or electronically, about exam content while the exam is in progress.
Audible conversation, reading exam questions aloud, or receiving spoken
answers from another person are all violations.

RULE 5: Laptops, tablets, smart speakers, and other secondary computing
devices are prohibited unless the exam instructions explicitly permit a
named secondary device (e.g. a calculator app on a locked-down tablet).

RULE 6: Candidates must remain visible to the proctoring camera for the
full duration of the exam. Leaving the frame for an extended period
without prior authorization is a violation.

RULE 7: Use of remote controls, external keyboards, or external mice not
belonging to the authorized exam device is prohibited, as these can
indicate an unauthorized secondary computer or screen-sharing setup.

RULE 8: Any evidence gathered by the proctoring system is preliminary and
automated. A human reviewer must confirm a violation before disciplinary
action is taken; automated detections alone do not constitute proof of
misconduct.
"""


import re
from typing import List

# Splits on "RULE N:" boundaries rather than a fixed word count. A generic
# word-count chunker (chunk_size=80, overlap=20) is meant for large,
# unstructured documents -- on a short, already-structured text like this
# one it produces a handful of near-duplicate, heavily overlapping chunks
# (25% overlap on a ~230-word doc), and top_k=5 retrieval then returns
# almost the whole document multiple times. Splitting on the text's own
# RULE markers gives one clean, non-overlapping chunk per rule instead.
_RULE_BOUNDARY = re.compile(r"(?=RULE \d+:)")


def split_into_rule_chunks(text: str = EXAM_RULES_TEXT) -> List[str]:
    """Split EXAM_RULES_TEXT into one chunk per RULE N: entry."""
    return [part.strip() for part in _RULE_BOUNDARY.split(text.strip()) if part.strip()]
