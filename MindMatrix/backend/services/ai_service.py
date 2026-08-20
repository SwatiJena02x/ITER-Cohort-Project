# ============================================================
# ai_service.py
#
# Purpose:
# ------------------------------------------------------------
# Central AI service for the DSA Coach application.
#
# Responsibilities:
#   1. Connect to Groq
#   2. Send prompts to the LLM
#   3. Return generated text
#
# Used by:
#   - Feedback generation
#   - AI DSA hints
#
# Architecture:
#
# FastAPI
#    |
#    v
# Service Layer
#    |
#    v
# ai_service.py
#    |
#    v
# Groq API
#    |
#    v
# LLM
# ============================================================


from openai import OpenAI

from config.settings import GROQ_API_KEY, MODEL


# ============================================================
# GROQ CLIENT
# ============================================================

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)


# ============================================================
# GENERIC AI GENERATION FUNCTION
# ============================================================
#
# This is the main function used by the Hint API.
#
# Input:
#   prompt -> complete prompt for the LLM
#
# Output:
#   generated text
#
# ============================================================

def generate(prompt: str) -> str:

    if not prompt or not prompt.strip():
        raise ValueError("AI prompt cannot be empty.")

    response = client.chat.completions.create(

        model=MODEL,

        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert DSA interview coach. "
                    "Give accurate, concise and educational "
                    "answers. Never reveal a complete solution "
                    "when the user asks for a hint."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],

        temperature=0.3,

    )

    # --------------------------------------------------------
    # Safely extract generated text
    # --------------------------------------------------------

    if not response.choices:

        raise RuntimeError(
            "The AI model returned no choices."
        )

    content = response.choices[0].message.content

    if not content:

        raise RuntimeError(
            "The AI model returned an empty response."
        )

    return content.strip()


# ============================================================
# GET AI FEEDBACK
# ============================================================
#
# Kept for compatibility with your existing project.
#
# Existing code may call:
#
#     get_ai_feedback(prompt)
#
# ============================================================

def get_ai_feedback(prompt: str) -> str:

    return generate(prompt)


# ============================================================
# GET AI HINT
# ============================================================
#
# Dedicated function for progressive DSA hints.
#
# ============================================================

def get_ai_hint(prompt: str) -> str:

    return generate(prompt)


# ============================================================
# END OF ai_service.py
# ============================================================