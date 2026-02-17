#!/bin/bash
# ============================================
# CV Builder - Docker Build Helper (Linux/Mac)
# ============================================

set -e

echo ""
echo "============================================"
echo "CV Builder - Docker Build Helper"
echo "============================================"
echo ""

# Check if Docker is running
if ! docker version >/dev/null 2>&1; then
    echo "[ERROR] Docker is not running!"
    echo "Please start Docker and try again."
    exit 1
fi
echo "[OK] Docker is running"
echo ""

show_menu() {
    echo "Choose build option:"
    echo ""
    echo "1. Build with main Dockerfile (includes WeasyPrint)"
    echo "2. Build with simple Dockerfile (no WeasyPrint, more reliable)"
    echo "3. Build with no cache (force clean build)"
    echo "4. Test with docker-compose"
    echo "5. Clean Docker cache and rebuild"
    echo "6. Exit"
    echo ""
}

while true; do
    show_menu
    read -p "Enter choice (1-6): " choice
    echo ""

    case $choice in
        1)
            echo "Building with main Dockerfile..."
            if docker build -t cvbuilder:latest .; then
                echo ""
                echo "[SUCCESS] Build completed!"
                echo ""
                echo "To run: docker run -p 8000:8000 cvbuilder:latest"
            else
                echo ""
                echo "[ERROR] Build failed!"
                echo "Try option 2 for simpler build or option 5 to clean cache."
            fi
            echo ""
            read -p "Press Enter to continue..."
            ;;
        2)
            echo "Building with simple Dockerfile (no WeasyPrint)..."
            if docker build -f Dockerfile.simple -t cvbuilder:simple .; then
                echo ""
                echo "[SUCCESS] Build completed!"
                echo "Note: PDF download disabled, but Print to PDF works!"
                echo ""
                echo "To run: docker run -p 8000:8000 cvbuilder:simple"
            else
                echo ""
                echo "[ERROR] Build failed!"
            fi
            echo ""
            read -p "Press Enter to continue..."
            ;;
        3)
            echo "Building with no cache..."
            if docker build --no-cache -t cvbuilder:latest .; then
                echo ""
                echo "[SUCCESS] Build completed!"
            else
                echo ""
                echo "[ERROR] Build failed!"
            fi
            echo ""
            read -p "Press Enter to continue..."
            ;;
        4)
            echo "Starting with docker-compose..."
            docker-compose up --build
            ;;
        5)
            echo "Cleaning Docker cache..."
            docker builder prune -af
            echo ""
            echo "[OK] Cache cleaned"
            echo ""
            echo "Now rebuilding..."
            if docker build -t cvbuilder:latest .; then
                echo ""
                echo "[SUCCESS] Build completed!"
            else
                echo ""
                echo "[ERROR] Build failed!"
            fi
            echo ""
            read -p "Press Enter to continue..."
            ;;
        6)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid choice, please try again."
            ;;
    esac
done
