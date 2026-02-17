# ============================================
# CV Builder - Production Dockerfile (Fixed)
# ============================================
# Simplified and more robust build process

FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies (split into manageable steps)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        # Build essentials
        gcc \
        g++ \
        # PostgreSQL client library
        libpq-dev \
        libpq5 \
        # WeasyPrint dependencies
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf2.0-0 \
        libffi-dev \
        libcairo2 \
        # Fonts for PDF generation
        fontconfig \
        fonts-liberation \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Update font cache for WeasyPrint
RUN fc-cache -fv

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# Initialize database and start server
CMD python -c "from app import create_app; from app.extensions import db; \
    app = create_app('production'); \
    app.app_context().push(); \
    db.create_all(); \
    print('✓ Database initialized')" && \
    gunicorn \
        --bind 0.0.0.0:8000 \
        --workers ${WEB_CONCURRENCY:-2} \
        --threads 4 \
        --worker-class gthread \
        --worker-tmp-dir /dev/shm \
        --timeout 120 \
        --graceful-timeout 30 \
        --keep-alive 5 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        "app:create_app()"
