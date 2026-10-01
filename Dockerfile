FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=5050

WORKDIR /app

# Install system build dependencies for ReportLab & Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose HTTP port
EXPOSE 5050

# Healthcheck to verify server uptime
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://127.0.0.1:5050/api/venues || exit 1

# Launch production Gunicorn WSGI server
CMD ["gunicorn", "-c", "gunicorn.conf.py", "src.app:app"]
