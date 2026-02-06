#!/usr/bin/env python3
"""Run the PDF Converter web application"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.app import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
