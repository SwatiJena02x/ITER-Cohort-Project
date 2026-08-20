# ==========================================================
# prompt_service.py
#
# Purpose:
# Reads the prompt template from a file and fills in the
# user's problem, language, code, and approach.
# ==========================================================

# Import FeedbackRequest schema.
from schemas.request import FeedbackRequest


def build_prompt(request: FeedbackRequest):

    # Open the prompt template file.
    with open(
        "prompts/feedback_prompt.txt",
        "r",
        encoding="utf-8"
    ) as file:

        prompt = file.read()

    # Replace placeholders with actual values.
    prompt = prompt.replace("{problem}", request.problem)
    prompt = prompt.replace("{language}", request.language)
    prompt = prompt.replace("{code}", request.code)
    prompt = prompt.replace("{approach}", request.approach)

    # Return the completed prompt.
    return prompt