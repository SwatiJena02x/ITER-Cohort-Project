FROM python:3.11-slim

WORKDIR /app

# System dependencies required by OpenCV,
# face-recognition/dlib and MediaPipe
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-6 \
    libglib2.0-0 \
    libgl1 \
    libsm6 \
    libxext6 \
    libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir --timeout 300 --retries 10 -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
