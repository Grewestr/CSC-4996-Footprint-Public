# Dockerfile
FROM python:3.10-slim

WORKDIR /AI_Scripts

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies, including those for Image_classification and CSV_To_Firestore
RUN pip install --no-cache-dir \
    torch \
    opencv-python-headless \
    numpy \
    yt-dlp \
    redis \
    rq \
    inference_sdk \
    pandas \
    scikit-learn \
    colormath \
    google-cloud-firestore \
    firebase-admin

# Copy app code
COPY . .

# Environment variable for Redis
ENV REDIS_URL=redis://redis-server:6379/0

# Start worker with scheduler
CMD ["rq", "worker", "--with-scheduler"]
