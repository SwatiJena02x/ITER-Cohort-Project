# ==========================================================
# File Name : json_parser.py
#
# Purpose:
# --------
# AI models sometimes return extra text along with JSON.
#
# Example:
#
# Sure! Here's your feedback.
#
# {
#     "overall_score":9.5
# }
#
# This file extracts only the JSON part so that
# json.loads() can successfully parse it.
#
# ==========================================================


# Import json module.
# Used to convert JSON string into Python dictionary.
import json


# Import Regular Expression module.
# It helps us search patterns inside a string.
import re



# ==========================================================
# Function Name:
# parse_ai_response()
#
# Purpose:
# --------
# Accept the raw AI response.
#
# Remove unnecessary text.
#
# Extract JSON.
#
# Convert JSON string into Python dictionary.
#
# Return dictionary.
# ==========================================================
def parse_ai_response(ai_response: str):


    # ---------------------------------------------
    # Remove leading and trailing spaces.
    #
    # Example
    #
    # "   Hello   "
    #
    # becomes
    #
    # "Hello"
    # ---------------------------------------------
    ai_response = ai_response.strip()



    # ---------------------------------------------
    # Search for the first JSON object.
    #
    # Pattern:
    #
    # \{.*\}
    #
    # Meaning:
    #
    # \{
    #     Start with {
    #
    # .* 
    #     Match everything
    #
    # \}
    #     End with }
    #
    # re.DOTALL allows "." to match multiple lines.
    # ---------------------------------------------
    match = re.search(

        r"\{.*\}",

        ai_response,

        re.DOTALL

    )



    # ---------------------------------------------
    # If JSON is not found,
    # raise an exception.
    # ---------------------------------------------
    if not match:

        raise ValueError(

            "No valid JSON found in AI response."

        )



    # ---------------------------------------------
    # Extract JSON text.
    #
    # Example
    #
    # Sure!
    #
    # {
    #   ...
    # }
    #
    # becomes only
    #
    # {
    #   ...
    # }
    # ---------------------------------------------
    json_text = match.group()



    # ---------------------------------------------
    # Convert JSON string
    #
    # into
    #
    # Python Dictionary.
    # ---------------------------------------------
    data = json.loads(

        json_text

    )



    # ---------------------------------------------
    # Return dictionary.
    # ---------------------------------------------
    return data