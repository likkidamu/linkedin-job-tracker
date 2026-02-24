FROM python:3.12-slim

# WeasyPrint system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY config.py .
COPY database.py .
COPY scraper.py .
COPY resume_tailor.py .
COPY pdf_generator.py .
COPY main.py .
COPY base_resume.json .
COPY templates/ templates/

# Create data and output directories
RUN mkdir -p /app/data /app/output

# Volumes for persistent data
VOLUME ["/app/data", "/app/output"]

CMD ["python", "main.py"]
