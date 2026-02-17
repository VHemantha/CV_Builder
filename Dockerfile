# ============================================
# CV Builder - Production Dockerfile
# ============================================
# Multi-stage build for optimized production image

# ============================================
# Stage 1: Build Stage
# ============================================
FROM python:3.12-slim as builder

# Set build-time environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install build dependencies for WeasyPrint and psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libpq-dev \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf2.0-0 \
        libffi-dev \
        libcairo2 \
        libcairo2-dev \
        shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --user --no-warn-script-location -r requirements.txt

# ============================================
# Stage 2: Runtime Stage
# ============================================
FROM python:3.12-slim

# Set runtime environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PATH=/home/appuser/.local/bin:$PATH

WORKDIR /app

# Install only runtime dependencies (no build tools)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq5 \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf2.0-0 \
        libffi8 \
        libcairo2 \
        shared-mime-info \
        fonts-liberation \
        fontconfig \
    && fc-cache -fv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy Python packages from builder stage
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port 8000 for gunicorn
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Run database migrations and start gunicorn
CMD python -c "from app import create_app; from app.extensions import db; app = create_app('production'); \
    with app.app_context(): db.create_all(); print('✓ Database initialized')" && \
    gunicorn \
        --bind 0.0.0.0:8000 \
        --workers 2 \
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
        --capture-output \
        "app:create_app()"
