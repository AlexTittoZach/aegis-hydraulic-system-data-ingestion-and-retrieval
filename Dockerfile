# Aegis Knowledge Ingestion & Hybrid RAG System — Air-Gapped Docker Container
# Provides 100% on-premise execution with zero external network connectivity.

FROM python:3.12-slim

# Install system dependencies: build essentials for llama-cpp-python, curl, OCR & PDF utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    curl \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download model weights and pre-cache embeddings during image build
# Once built, the container image is 100% self-contained and air-gapped
COPY download_models.py .
RUN python3 download_models.py

# Copy application codebase and knowledge representations
COPY . .

# Run benchmark evaluation during build to verify container integrity
RUN python3 evaluate.py

# Expose Streamlit port
EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Default command launches the interactive Web UI
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
