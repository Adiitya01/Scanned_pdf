#!/bin/bash

echo "======================================"
echo "PDF Converter - Quick Setup Script"
echo "======================================"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python
echo "Checking Python installation..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "✓ Python $PYTHON_VERSION found"
else
    echo "✗ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check pip
echo "Checking pip installation..."
if command_exists pip3; then
    echo "✓ pip3 found"
else
    echo "✗ pip3 not found. Please install pip3."
    exit 1
fi

# Detect OS
echo ""
echo "Detecting operating system..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo "✓ Linux detected"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
    echo "✓ macOS detected"
else
    OS="unknown"
    echo "! Unknown OS. Manual installation may be required."
fi

# Install system dependencies
echo ""
echo "Installing system dependencies..."
if [ "$OS" == "linux" ]; then
    echo "Installing Tesseract OCR and Poppler..."
    sudo apt-get update
    sudo apt-get install -y tesseract-ocr tesseract-ocr-eng poppler-utils
    
    # Ask about additional languages
    read -p "Install additional OCR languages? (y/n): " install_langs
    if [ "$install_langs" == "y" ]; then
        echo "Installing common language packs..."
        sudo apt-get install -y \
            tesseract-ocr-fra \
            tesseract-ocr-deu \
            tesseract-ocr-spa \
            tesseract-ocr-ita \
            tesseract-ocr-por
    fi
elif [ "$OS" == "mac" ]; then
    if command_exists brew; then
        echo "Installing via Homebrew..."
        brew install tesseract poppler
    else
        echo "! Homebrew not found. Please install Tesseract and Poppler manually."
        echo "  Tesseract: https://github.com/tesseract-ocr/tesseract"
        echo "  Poppler: https://poppler.freedesktop.org/"
    fi
fi

# Verify Tesseract installation
echo ""
echo "Verifying Tesseract OCR..."
if command_exists tesseract; then
    TESSERACT_VERSION=$(tesseract --version 2>&1 | head -n 1)
    echo "✓ $TESSERACT_VERSION"
else
    echo "✗ Tesseract not found. OCR features will not work."
fi

# Verify Poppler installation
echo ""
echo "Verifying Poppler utils..."
if command_exists pdftoppm; then
    echo "✓ Poppler utils installed"
else
    echo "✗ Poppler utils not found. PDF to image conversion will not work."
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt --break-system-packages 2>/dev/null || \
pip3 install -r requirements.txt

# Verify Python packages
echo ""
echo "Verifying Python packages..."
python3 -c "import pypdf; print('✓ pypdf installed')" 2>/dev/null || echo "✗ pypdf not installed"
python3 -c "import pdfplumber; print('✓ pdfplumber installed')" 2>/dev/null || echo "✗ pdfplumber not installed"
python3 -c "import pytesseract; print('✓ pytesseract installed')" 2>/dev/null || echo "✗ pytesseract not installed"
python3 -c "import pdf2image; print('✓ pdf2image installed')" 2>/dev/null || echo "✗ pdf2image not installed"
python3 -c "import docx; print('✓ python-docx installed')" 2>/dev/null || echo "✗ python-docx not installed"
python3 -c "import flask; print('✓ Flask installed')" 2>/dev/null || echo "✗ Flask not installed"

# Create test file
echo ""
echo "Setup complete!"
echo ""
echo "======================================"
echo "Quick Start:"
echo "======================================"
echo ""
echo "1. Start the web interface:"
echo "   python3 app.py"
echo "   Then open: http://localhost:5000"
echo ""
echo "2. Or use the command line:"
echo "   python3 pdf_converter.py your_file.pdf"
echo ""
echo "3. For help:"
echo "   python3 pdf_converter.py --help"
echo ""
echo "======================================"
