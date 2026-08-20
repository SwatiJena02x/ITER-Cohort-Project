# ==========================================================
# File Name : feedback_service.py
#
# Purpose:
# --------
# This file contains the main business logic of the
# DSA Coach Feedback Generator.
#
# Responsibilities:
# 1. Generate AI prompt.
# 2. Send prompt to the AI model.
# 3. Receive AI response.
# 4. Parse AI response safely.
# 5. Return structured feedback.
# ==========================================================


# Import request schema.
# This schema contains the user's submitted data.
from schemas.request import FeedbackRequest


# Import response schema.
# This schema defines the format of the API response.
from schemas.response import FeedbackResponse


# Import prompt builder.
# This function creates the prompt for the AI.
from services.prompt_service import build_prompt


# Import AI service.
# Sends the prompt to Groq/OpenAI.
from services.ai_service import get_ai_feedback


# Import JSON parser.
# Extracts valid JSON from the AI response.
from utils.json_parser import parse_ai_response



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
# User Input
#      │
#      ▼
# Build Prompt
#      │
#      ▼
# Send Prompt to AI
#      │
#      ▼
# Receive AI Response
#      │
#      ▼
# Parse JSON
#      │
#      ▼
# Create FeedbackResponse
#      │
#      ▼
# Return Response
# ==========================================================
def generate_feedback(request: FeedbackRequest):


    # --------------------------------------------
    # STEP 1
    # Build the prompt using the user's submission.
    # --------------------------------------------
    prompt = build_prompt(request)


    # Print prompt for debugging.
    print("\n========== GENERATED PROMPT ==========\n")
    print(prompt)



    # --------------------------------------------
    # STEP 2
    # Send the prompt to the AI model.
    # --------------------------------------------
    ai_response = get_ai_feedback(prompt)


    # Print AI response.
    print("\n========== RAW AI RESPONSE ==========\n")
    print(ai_response)



    # --------------------------------------------
    # STEP 3
    # Parse the AI response.
    #
    # This function removes extra text and extracts
    # only the JSON object.
    # --------------------------------------------
    try:

        data = parse_ai_response(ai_response)

    except Exception as error:

        print("\nJSON Parsing Error")
        print(error)


        # Return default response if parsing fails.
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



    # --------------------------------------------
    # STEP 4
    # Create FeedbackResponse object.
    #
    # Pydantic validates every field automatically.
    # --------------------------------------------
    feedback = FeedbackResponse(

        overall_score=data["overall_score"],

        time_complexity=data["time_complexity"],

        space_complexity=data["space_complexity"],

        strengths=data["strengths"],

        weaknesses=data["weaknesses"],

        suggestions=data["suggestions"],

        interview_result=data["interview_result"]

    )



    # --------------------------------------------
    # STEP 5
    # Return validated feedback.
    # --------------------------------------------
    return feedback