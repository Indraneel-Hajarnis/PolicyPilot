FROM python:3.11-slim

# Install system dependencies for PyMuPDF and general build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (Docker cache layer)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code + seed data
COPY . ./

# Pre-download the embedding model during build (~120MB)
# Avoids cold-start model download in production
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"

# Pre-compute FAISS index + SQLite DB from seed_data/ during build
# This means the Docker image ships with all data ready — instant cold starts
RUN mkdir -p /app/data/uploads /app/data/faiss_index && \
    python scripts/preseed.py

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
