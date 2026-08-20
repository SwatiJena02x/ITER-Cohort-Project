# ============================================================
# DSA Coach AI - Backend Dockerfile
# ============================================================

# Use Python 3.10 because your local project is using Python 3.10
FROM python:3.10-slim

# Prevent Python from creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Show Python logs immediately
ENV PYTHONUNBUFFERED=1

# ------------------------------------------------------------
# Set working directory inside container
# ------------------------------------------------------------
WORKDIR /app

# ------------------------------------------------------------
# Install system dependencies
# ------------------------------------------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# Copy requirements first
# This improves Docker build caching
# ------------------------------------------------------------
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ------------------------------------------------------------
# Copy complete backend application
# ------------------------------------------------------------
COPY . .

# ------------------------------------------------------------
# Backend port
# ------------------------------------------------------------
EXPOSE 8000

# ------------------------------------------------------------
# Start FastAPI using Uvicorn
# ------------------------------------------------------------
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]