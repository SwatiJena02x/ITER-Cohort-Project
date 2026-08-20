# ============================================================
# config/settings.py
# ============================================================

import os
from dotenv import load_dotenv


# ============================================================
# Load .env file
# ============================================================

load_dotenv()


# ============================================================
# Settings Class
# ============================================================

class Settings:

    # Groq API key
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

    # Groq model
    MODEL = os.getenv(
        "MODEL",
        "llama-3.3-70b-versatile"
    )

    # Application settings
    APP_NAME = os.getenv(
        "APP_NAME",
        "DSA Coach AI"
    )

    ENVIRONMENT = os.getenv(
        "ENVIRONMENT",
        "development"
    )

    DEBUG = os.getenv(
        "DEBUG",
        "false"
    ).lower() == "true"


# ============================================================
# ⭐ CHANGE 1:
# Create settings object.
#
# This fixes:
#
# ImportError:
# cannot import name 'settings'
# ============================================================

settings = Settings()


# ============================================================
# ⭐ CHANGE 2:
# Keep these variables for ai_service.py
#
# ai_service.py uses:
#
# from config.settings import GROQ_API_KEY, MODEL
# ============================================================

GROQ_API_KEY = settings.GROQ_API_KEY
MODEL = settings.MODEL
APP_NAME = settings.APP_NAME
ENVIRONMENT = settings.ENVIRONMENT
DEBUG = settings.DEBUG