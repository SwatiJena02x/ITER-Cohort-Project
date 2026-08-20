# ==========================================================
# File Name : feedback_service.py
#
# Purpose:
# ----------------------------------------------------------
# This file contains the business logic of the application.
#
# Responsibilities:
# 1. Build AI prompt.
# 2. Send prompt to AI model.
# 3. Receive AI response.
# 4. Parse AI response safely.
# 5. Validate response.
# 6. Return structured feedback.
#
# ==========================================================


# ==========================================================
# Import FeedbackRequest schema.
# This contains the user's submitted problem,
# programming language, code, and approach.
# ==========================================================
from schemas.request import FeedbackRequest


# ==========================================================
# Import FeedbackResponse schema.
# This defines the JSON response returned
# to the frontend.
# ==========================================================
from schemas.response import FeedbackResponse


# ==========================================================
# Import prompt builder.
# Creates the prompt sent to the AI model.
# ==========================================================
from services.prompt_service import build_prompt


# ==========================================================
# Import AI service.
# Sends prompt to Groq/OpenAI and receives
# the generated response.
# ==========================================================
from services.ai_service import get_ai_feedback


# ==========================================================
# Import JSON parser.
# Cleans AI response and extracts valid JSON.
# ==========================================================
from utils.json_parser import parse_ai_response


# ==========================================================
# Import logger.
# Used instead of print() for debugging.
# ==========================================================
from utils.logger import logger


# ==========================================================
# Function Name:
# generate_feedback()
#
# Input:
# -------
# FeedbackRequest
#
# Output:
# --------
# FeedbackResponse
#
# Workflow:
#
# User Request
#      │
#      ▼
# Build Prompt
#      │
#      ▼
# Send Prompt
#      │
#      ▼
# Receive AI Response
#      │
#      ▼
# Parse JSON
#      │
#      ▼
# Validate Data
#      │
#      ▼
# Return FeedbackResponse
#
# ==========================================================
def generate_feedback(request: FeedbackRequest):

    # ======================================================
    # STEP 1
    # Build prompt from user's submission.
    # ======================================================
    prompt = build_prompt(request)

    logger.info("========== GENERATED PROMPT ==========")
    logger.info(prompt)



    # ======================================================
    # STEP 2
    # Send prompt to AI model.
    # ======================================================
    ai_response = get_ai_feedback(prompt)

    logger.info("========== RAW AI RESPONSE ==========")
    logger.info(ai_response)



    # ======================================================
    # STEP 3
    # Parse AI response.
    #
    # Removes extra text like:
    #
    # Sure!
    #
    # {
    #   ...
    # }
    #
    # and extracts only JSON.
    # ======================================================
    try:

        data = parse_ai_response(ai_response)

    except Exception as error:

        logger.error("JSON Parsing Failed")
        logger.error(error)

        # Return default response.
        return FeedbackResponse(

            overall_score=0,

            time_complexity="Unknown",

            space_complexity="Unknown",

            strengths=[],

            weaknesses=[
                "Unable to parse AI response."
            ],

            suggestions=[
                "Please try again."
            ],

            interview_result="Failed"

        )



    # ======================================================
    # STEP 4
    # Validate AI response.
    #
    # Pydantic automatically checks:
    #
    # overall_score
    # time_complexity
    # strengths
    # etc.
    #
    # If anything is missing,
    # ValidationError will occur.
    # ======================================================
    try:

        feedback = FeedbackResponse(**data)

    except Exception as error:

        logger.error("Response Validation Failed")
        logger.error(error)

        return FeedbackResponse(

            overall_score=0,

            time_complexity="Unknown",

            space_complexity="Unknown",

            strengths=[],

            weaknesses=[
                "Invalid response format received from AI."
            ],

            suggestions=[
                "Please try again."
            ],

            interview_result="Failed"

        )



    # ======================================================
    # STEP 5
    # Return validated response.
    # ======================================================
    logger.info("========== FEEDBACK GENERATED ==========")

    return feedback