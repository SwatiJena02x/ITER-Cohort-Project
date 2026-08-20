# ============================================================
# request.py
#
# Purpose:
# Defines API request format.
# ============================================================

from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    """Request payload for generating DSA coach feedback."""

    problem: str = Field(
        ...,
        min_length=1,
        description="Name of the DSA problem (e.g. 'Two Sum', 'Merge Intervals').",
        examples=["Two Sum"],
    )

    language: str = Field(
        ...,
        min_length=1,
        description="Programming language the solution is written in.",
        examples=["Python"],
    )

    code: str = Field(
        ...,
        min_length=1,
        description="User's source code submission.",
        examples=["def two_sum(nums, target):\n    ..."],
    )

    approach: str = Field(
        ...,
        min_length=1,
        description="User's explanation of their approach / thought process.",
        examples=["I used a hashmap to store complements while iterating once."],
    )

    class Config:
        json_schema_extra = {
            "example": {
                "problem": "Two Sum",
                "language": "Python",
                "code": "def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target - n in seen:\n            return [seen[target - n], i]\n        seen[n] = i",
                "approach": "I used a hashmap to store complements while iterating once for O(n) time.",
            }
        }