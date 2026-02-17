#!/bin/bash
# ============================================
# Quick Docker Run Script (Linux/Mac)
# ============================================

echo ""
echo "============================================"
echo "CV Builder - Quick Docker Run"
echo "============================================"
echo ""

# Check if image exists
if ! docker image inspect cvbuilder >/dev/null 2>&1; then
    echo "Image 'cvbuilder' not found. Building..."
    docker build -f Dockerfile.simple -t cvbuilder .
    if [ $? -ne 0 ]; then
        echo "[ERROR] Build failed!"
        exit 1
    fi
fi

echo ""
echo "Starting CV Builder with SQLite..."
echo ""
echo "Access the app at: http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""

docker run -it --rm \
  -p 8000:8000 \
  -e DATABASE_URL=sqlite:////app/cv_builder.db \
  -e REDIS_URL= \
  -e SECRET_KEY=dev-secret-key-change-me \
  -e IP_HASH_SALT=dev-salt \
  -e GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID:-your_google_client_id_here} \
  -e GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET:-your_google_client_secret_here} \
  -e OAUTHLIB_INSECURE_TRANSPORT=1 \
  -e APP_BASE_URL=http://localhost:8000 \
  -e MAX_CVS_PER_USER=10 \
  -e TALISMAN_FORCE_HTTPS=false \
  cvbuilder

echo ""
echo "Container stopped."
