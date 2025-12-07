# brandguard/backend/Dockerfile (Updated)
FROM python:3.11-slim

# Install system dependencies from requirements
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    netcat \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1

# Run as non-root
USER appuser

# Expose port
EXPOSE 8000

# Run with gunicorn for production
CMD ["gunicorn", "app.main:brandguarded_app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--timeout", "300"]