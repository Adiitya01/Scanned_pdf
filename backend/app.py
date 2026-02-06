#!/usr/bin/env python3
"""
PDF Converter - Main Flask Application
Serves frontend and API
"""

import tempfile
from pathlib import Path

from flask import Flask, send_from_directory

from .api import init_api

# Paths
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_ROOT / 'frontend'
UPLOAD_FOLDER = Path(tempfile.gettempdir()) / 'pdf_converter_uploads'
OUTPUT_FOLDER = Path(tempfile.gettempdir()) / 'pdf_converter_outputs'

UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

app = Flask(__name__)
app.secret_key = 'pdf-converter-secret-key-change-in-production'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# Register API routes
init_api(app, UPLOAD_FOLDER, OUTPUT_FOLDER)


@app.route('/')
def index():
    """Serve frontend"""
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/css/<path:filename>')
def frontend_css(filename):
    """Serve CSS files"""
    return send_from_directory(FRONTEND_DIR / 'css', filename)


@app.route('/js/<path:filename>')
def frontend_js(filename):
    """Serve JS files"""
    return send_from_directory(FRONTEND_DIR / 'js', filename)


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("PDF Converter - Searchable PDF Generator")
    print("=" * 60)
    print("\n  Frontend: http://localhost:5000")
    print("  API:      http://localhost:5000/api/")
    print("\n  Press Ctrl+C to stop")
    print("=" * 60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
