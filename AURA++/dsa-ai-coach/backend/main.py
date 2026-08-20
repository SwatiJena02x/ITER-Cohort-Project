from fastapi import FastAPI

app = FastAPI(
    title="DSA AI Coach",
    description="AI-powered Dynamic Programming learning platform",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to DSA AI Coach",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }