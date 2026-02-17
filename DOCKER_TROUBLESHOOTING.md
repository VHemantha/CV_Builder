# Docker Build Troubleshooting Guide

If you're experiencing Docker build failures, follow this guide.

## Common Error: apt-get exit code 100

**Error Message**:
```
failed to solve: process "/bin/sh -c apt-get update && apt-get install..."
did not complete successfully: exit code: 100
```

### Solutions (Try in Order)

#### Solution 1: Clear Docker Cache

```bash
# Clear Docker build cache
docker builder prune -af

# Rebuild
docker build -t cvbuilder .
```

#### Solution 2: Update Docker Desktop

1. Check Docker Desktop version
2. Update to latest version
3. Restart Docker Desktop
4. Try build again

#### Solution 3: Use Simple Dockerfile

If WeasyPrint dependencies are causing issues:

```bash
# Use simple Dockerfile (no WeasyPrint)
docker build -f Dockerfile.simple -t cvbuilder .

# Or for Render deployment, edit render.yaml:
# Change: dockerfilePath: ./Dockerfile
# To: dockerfilePath: ./Dockerfile.simple
```

**Note**: Without WeasyPrint, PDF download will not work, but Print to PDF from browser still works perfectly!

#### Solution 4: Build with No Cache

```bash
# Force rebuild without cache
docker build --no-cache -t cvbuilder .
```

#### Solution 5: Use Docker Buildx

```bash
# Use buildx for better compatibility
docker buildx build --platform linux/amd64 -t cvbuilder .
```

#### Solution 6: Alternative Base Image

Create `Dockerfile.alpine`:

```dockerfile
FROM python:3.12-alpine

RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libffi-dev

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || \
    (grep -v weasyprint requirements.txt > req-minimal.txt && \
     pip install --no-cache-dir -r req-minimal.txt)

COPY . .
RUN adduser -D appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:create_app()"]
```

Then build:
```bash
docker build -f Dockerfile.alpine -t cvbuilder .
```

## Render.com Deployment Issues

### If Build Fails on Render

**Option 1**: Use Simple Dockerfile
1. Edit `render.yaml`
2. Change: `dockerfilePath: ./Dockerfile`
3. To: `dockerfilePath: ./Dockerfile.simple`
4. Git commit and push
5. Render will rebuild automatically

**Option 2**: Use Native Python Runtime
1. Edit `render.yaml`
2. Change: `runtime: docker`
3. To: `runtime: python3`
4. Add: `buildCommand: pip install -r requirements.txt`
5. Git commit and push

Example:
```yaml
services:
  - type: web
    name: cv-builder
    runtime: python3  # Changed from docker
    # Remove dockerfilePath line
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT app:create_app()
```

## Testing Locally

### Test Without Docker

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run locally
python run_local.py

# Access at http://localhost:5000
```

### Test with Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f web

# If it fails, check individual services
docker-compose ps
docker-compose logs db
docker-compose logs redis
docker-compose logs web

# Stop and clean up
docker-compose down -v
```

## Windows-Specific Issues

### WSL2 Backend Issues

If using Docker Desktop with WSL2:

```bash
# In WSL2 terminal
# Update WSL
wsl --update

# Restart Docker Desktop

# Try build again
docker build -t cvbuilder .
```

### Hyper-V Issues

If on Hyper-V backend:
1. Open Docker Desktop Settings
2. Resources → Advanced
3. Increase Memory to at least 4GB
4. Increase CPUs to at least 2
5. Click "Apply & Restart"
6. Try build again

## Network Issues

### Proxy/Firewall

If behind corporate proxy:

```bash
# Build with proxy
docker build \
  --build-arg HTTP_PROXY=http://proxy:port \
  --build-arg HTTPS_PROXY=http://proxy:port \
  -t cvbuilder .
```

### DNS Issues

Add to Dockerfile before apt-get:
```dockerfile
RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf && \
    echo "nameserver 8.8.4.4" >> /etc/resolv.conf
```

## Quick Fix: Deploy Without Docker

### For Render.com

Create `render-native.yaml`:

```yaml
services:
  - type: web
    name: cv-builder
    runtime: python3
    buildCommand: |
      pip install --upgrade pip
      pip install -r requirements.txt
    startCommand: |
      python -c "from app import create_app; from app.extensions import db; app = create_app('production'); app.app_context().push(); db.create_all()" &&
      gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 app:create_app()
    envVars:
      # ... (same as before)
```

Rename and use:
```bash
mv render.yaml render-docker.yaml
mv render-native.yaml render.yaml
git add .
git commit -m "Use native Python runtime"
git push
```

## Still Having Issues?

### Check Docker Status

```bash
# Check Docker is running
docker version

# Check Docker info
docker info

# Check available space
docker system df
```

### Clean Docker System

```bash
# Remove all unused data
docker system prune -a

# Remove all volumes
docker volume prune

# Restart Docker Desktop
```

### Alternative: Deploy to Heroku

If Render.com Docker builds keep failing, try Heroku:

1. Create `Procfile`:
   ```
   web: gunicorn app:create_app()
   ```

2. Create `runtime.txt`:
   ```
   python-3.12.0
   ```

3. Deploy:
   ```bash
   heroku create cv-builder
   heroku addons:create heroku-postgresql:mini
   heroku addons:create heroku-redis:mini
   git push heroku main
   ```

## Get Help

If none of these solutions work:

1. **Check Render Status**: https://status.render.com
2. **Render Support**: https://render.com/docs/support
3. **Docker Forums**: https://forums.docker.com
4. **GitHub Issues**: Open issue with error logs

## Recommended Approach

For simplest deployment:

1. **Use `Dockerfile.simple`** (no WeasyPrint)
2. **Print to PDF works via browser** (no download button)
3. **Much faster build times**
4. **Fewer dependencies to manage**
5. **More reliable on all platforms**

Edit `render.yaml`:
```yaml
dockerfilePath: ./Dockerfile.simple
```

This sacrifices the "Download PDF" feature but keeps 100% of core functionality with browser print-to-PDF.

---

**Last Updated**: 2026-02-17
