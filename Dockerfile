# Aegis Knowledge Ingestion System — Docker Container
# Provides 100% air-gapped, on-premise execution with zero external data exfiltration.

FROM python:3.12-slim

# Install system dependencies: local Tesseract OCR & poppler-utils (pdftoppm)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy dataset and application codebase
COPY . .

# Ingest and build the intermediate knowledge representation inside container
RUN python3 src/build_knowledge_store.py && python3 evaluate.py

# Expose Streamlit port
EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Default command launches the interactive Web UI
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
