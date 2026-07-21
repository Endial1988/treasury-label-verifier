FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-eng && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

EXPOSE 8080
CMD ["uvicorn", "label_verifier.app:app", "--host", "0.0.0.0", "--port", "8080"]
