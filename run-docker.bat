@echo off
REM ============================================
REM Quick Docker Run Script (Windows)
REM ============================================

echo.
echo ============================================
echo CV Builder - Quick Docker Run
echo ============================================
echo.

REM Check if image exists
docker image inspect cvbuilder >nul 2>&1
if errorlevel 1 (
    echo Image 'cvbuilder' not found. Building...
    docker build -f Dockerfile.simple -t cvbuilder .
    if errorlevel 1 (
        echo [ERROR] Build failed!
        pause
        exit /b 1
    )
)

echo.
echo Starting CV Builder with SQLite...
echo.
echo Access the app at: http://localhost:8000
echo Press Ctrl+C to stop
echo.

docker run -it --rm ^
  -p 8000:8000 ^
  -e DATABASE_URL=sqlite:////app/cv_builder.db ^
  -e REDIS_URL= ^
  -e SECRET_KEY=dev-secret-key-change-me ^
  -e IP_HASH_SALT=dev-salt ^
  -e GOOGLE_CLIENT_ID=your_google_client_id_here ^
  -e GOOGLE_CLIENT_SECRET=your_google_client_secret_here ^
  -e OAUTHLIB_INSECURE_TRANSPORT=1 ^
  -e APP_BASE_URL=http://localhost:8000 ^
  -e MAX_CVS_PER_USER=10 ^
  -e TALISMAN_FORCE_HTTPS=false ^
  cvbuilder

echo.
echo Container stopped.
pause
