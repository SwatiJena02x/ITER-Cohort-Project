# ============================================================
# main.py
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# Import API routers
# ============================================================

from api.feedback import router as feedback_router

# ============================================================
# ⭐ CHANGE:
# Import the hint router
# ============================================================

from api.hint import router as hint_router


# ============================================================
# Create FastAPI application
# ============================================================

app = FastAPI(

    title="DSA Coach AI",

    description="AI-powered DSA Interview Coach",

    version="1.0.0"

)


# ============================================================
# CORS
# ============================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)


# ============================================================
# ⭐ EXISTING:
# Feedback API
# ============================================================

app.include_router(
    feedback_router
)


# ============================================================
# ⭐ CHANGE:
# Register Hint API
#
# Without this line:
#
# POST /hint
#
# will return:
#
# 404 Not Found
# ============================================================

app.include_router(
    hint_router
)


# ============================================================
# Health Check
# ============================================================

@app.get("/health")
def health():

    return {

        "status": "ok",

        "service": "DSA Coach AI"

    }