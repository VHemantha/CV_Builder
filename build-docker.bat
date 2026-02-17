@echo off
REM ============================================
REM CV Builder - Docker Build Helper (Windows)
REM ============================================

echo.
echo ============================================
echo CV Builder - Docker Build Helper
echo ============================================
echo.

echo Checking Docker...
docker version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)
echo [OK] Docker is running
echo.

:menu
echo Choose build option:
echo.
echo 1. Build with main Dockerfile (includes WeasyPrint)
echo 2. Build with simple Dockerfile (no WeasyPrint, more reliable)
echo 3. Build with no cache (force clean build)
echo 4. Test with docker-compose
echo 5. Clean Docker cache and rebuild
echo 6. Exit
echo.

set /p choice="Enter choice (1-6): "

if "%choice%"=="1" goto main
if "%choice%"=="2" goto simple
if "%choice%"=="3" goto nocache
if "%choice%"=="4" goto compose
if "%choice%"=="5" goto clean
if "%choice%"=="6" goto end

echo Invalid choice, please try again.
goto menu

:main
echo.
echo Building with main Dockerfile...
docker build -t cvbuilder:latest .
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    echo Try option 2 for simpler build or option 5 to clean cache.
    pause
    goto menu
)
echo.
echo [SUCCESS] Build completed!
echo.
echo To run: docker run -p 8000:8000 cvbuilder:latest
pause
goto menu

:simple
echo.
echo Building with simple Dockerfile (no WeasyPrint)...
docker build -f Dockerfile.simple -t cvbuilder:simple .
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    echo Try option 5 to clean cache.
    pause
    goto menu
)
echo.
echo [SUCCESS] Build completed!
echo Note: PDF download disabled, but Print to PDF works!
echo.
echo To run: docker run -p 8000:8000 cvbuilder:simple
pause
goto menu

:nocache
echo.
echo Building with no cache...
docker build --no-cache -t cvbuilder:latest .
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    goto menu
)
echo.
echo [SUCCESS] Build completed!
pause
goto menu

:compose
echo.
echo Starting with docker-compose...
docker-compose up --build
goto menu

:clean
echo.
echo Cleaning Docker cache...
docker builder prune -af
echo.
echo [OK] Cache cleaned
echo.
echo Now rebuilding...
docker build -t cvbuilder:latest .
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    goto menu
)
echo.
echo [SUCCESS] Build completed!
pause
goto menu

:end
echo.
echo Goodbye!
exit /b 0
