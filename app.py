#!/usr/bin/env python3
"""
PDF Converter Web Application
Simple web interface for converting non-readable PDFs to readable formats
"""

from flask import Flask, render_template, request, send_file, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import sys
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

# Import the converter
sys.path.insert(0, os.path.dirname(__file__))
from pdf_converter import PDFConverter

app = Flask(__name__)
app.secret_key = 'pdf-converter-secret-key-change-in-production'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Create necessary directories
UPLOAD_FOLDER = Path(tempfile.gettempdir()) / 'pdf_converter_uploads'
OUTPUT_FOLDER = Path(tempfile.gettempdir()) / 'pdf_converter_outputs'
UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_old_files(folder, max_age_hours=24):
    """Remove files older than max_age_hours"""
    now = datetime.now()
    for file_path in folder.glob('*'):
        if file_path.is_file():
            try:
                age_hours = (now - datetime.fromtimestamp(file_path.stat().st_mtime)).total_seconds() / 3600
                if age_hours > max_age_hours:
                    file_path.unlink()
            except Exception as e:
                app.logger.warning(f"Cleanup failed for {file_path}: {e}")

@app.route('/')
def index():
    cleanup_old_files(UPLOAD_FOLDER)
    cleanup_old_files(OUTPUT_FOLDER)
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        input_path = UPLOAD_FOLDER / f"{timestamp}_{filename}"
        file.save(input_path)
        
        # Get conversion options
        output_format = request.form.get('format', 'pdf')
        force_ocr = request.form.get('force_ocr', 'false') == 'true'
        preserve_color = request.form.get('preserve_color', 'true') == 'true'
        dpi = int(request.form.get('dpi', 350))
        lang = request.form.get('lang', 'eng')

        # Convert PDF
        converter = PDFConverter(str(input_path), output_format)

        # Set output path
        ext = 'pdf' if output_format == 'pdf' else output_format
        suffix = '_searchable' if output_format == 'pdf' else '_converted'
        output_filename = Path(filename).stem + f'{suffix}.{ext}'
        output_path = OUTPUT_FOLDER / f"{timestamp}_{output_filename}"
        
        # Perform conversion
        converter.convert(
            force_ocr=force_ocr,
            dpi=dpi,
            lang=lang,
            output_path=str(output_path),
            preserve_color=preserve_color
        )
        
        # Clean up input file
        input_path.unlink()
        
        return jsonify({
            'success': True,
            'download_url': url_for('download_file', filename=output_path.name),
            'filename': output_filename
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    file_path = OUTPUT_FOLDER / filename
    if not file_path.exists():
        return "File not found", 404
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename.split('_', 1)[1] if '_' in filename else filename
    )

@app.route('/health')
def health_check():
    """Check if required dependencies are installed"""
    dependencies = {
        'pdfplumber': False,
        'pytesseract': False,
        'pdf2image': False,
        'docx': False
    }

    for dep in ['pdfplumber', 'pytesseract', 'pdf2image', 'docx']:
        try:
            __import__(dep)
            dependencies[dep] = True
        except ImportError:
            pass
    
    return jsonify(dependencies)


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("PDF Converter Web Application")
    print("=" * 60)
    print("\nStarting server at http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
