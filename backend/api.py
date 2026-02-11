"""
PDF Converter API - REST endpoints for conversion
"""

from pathlib import Path
from datetime import datetime
from flask import request, send_file, jsonify
from werkzeug.utils import secure_filename

from .pdf_converter import PDFConverter
from .docx_html import docx_to_html, html_to_docx


def init_api(app, upload_folder: Path, output_folder: Path):
    """Register API routes on the Flask app"""

    ALLOWED_EXTENSIONS = {'pdf'}

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def cleanup_old_files(folder: Path, max_age_hours: int = 24):
        """Remove files older than max_age_hours"""
        now = datetime.now()
        for file_path in folder.glob('*'):
            if file_path.is_file():
                try:
                    age_hours = (now - datetime.fromtimestamp(
                        file_path.stat().st_mtime)).total_seconds() / 3600
                    if age_hours > max_age_hours:
                        file_path.unlink()
                except Exception as e:
                    app.logger.warning(f"Cleanup failed for {file_path}: {e}")

    @app.route('/api/convert', methods=['POST'])
    def convert_pdf():
        """Convert uploaded PDF to searchable format"""
        cleanup_old_files(upload_folder)
        cleanup_old_files(output_folder)

        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Only PDF files are allowed'}), 400

        try:
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            input_path = upload_folder / f"{timestamp}_{filename}"
            file.save(input_path)

            output_format = request.form.get('format', 'pdf')
            force_ocr = request.form.get('force_ocr', 'false').lower() == 'true'
            preserve_color = request.form.get('preserve_color', 'true').lower() == 'true'
            dpi_raw = request.form.get('dpi', '350')
            try:
                dpi = int(dpi_raw) if dpi_raw else 350
            except (ValueError, TypeError):
                dpi = 350
            dpi = max(150, min(600, dpi))  # Clamp to valid range
            lang = request.form.get('lang', 'eng')

            converter = PDFConverter(str(input_path), output_format)

            ext = 'pdf' if output_format == 'pdf' else output_format
            suffix = '_searchable' if output_format == 'pdf' else '_converted'
            output_filename = Path(filename).stem + f'{suffix}.{ext}'
            output_path = output_folder / f"{timestamp}_{output_filename}"

            converter.convert(
                force_ocr=force_ocr,
                dpi=dpi,
                lang=lang,
                output_path=str(output_path),
                preserve_color=preserve_color
            )

            input_path.unlink()

            payload = {
                'success': True,
                'download_url': f'/api/download/{output_path.name}',
                'filename': output_filename
            }
            if output_format == 'docx':
                payload['edit_url'] = f'/editor?file={output_path.name}'
            return jsonify(payload)

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/download/<path:filename>')
    def download_file(filename):
        """Download converted file"""
        # Prevent path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({'error': 'Invalid filename'}), 400
        file_path = output_folder / filename
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404

        download_name = filename.split('_', 1)[1] if '_' in filename else filename
        return send_file(
            file_path,
            as_attachment=True,
            download_name=download_name
        )

    def _safe_docx_filename(name: str) -> bool:
        """Ensure filename is a safe basename and ends with .docx"""
        if '..' in name or '/' in name or '\\' in name:
            return False
        return name.strip().lower().endswith('.docx')

    @app.route('/api/document/<path:filename>/html', methods=['GET'])
    def document_to_html(filename):
        """Get DOCX file as HTML for the editor. No alignment changes."""
        if not _safe_docx_filename(filename):
            return jsonify({'error': 'Invalid filename'}), 400
        file_path = output_folder / filename
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        try:
            html = docx_to_html(file_path)
            return jsonify({'success': True, 'html': html})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/save-docx', methods=['POST'])
    def save_docx():
        """Save editor HTML as DOCX. Returns download URL. No alignment set."""
        try:
            data = request.get_json(force=True, silent=True) or {}
            html = data.get('html') or ''
            filename = data.get('filename') or 'edited.docx'
            if not isinstance(html, str):
                return jsonify({'success': False, 'error': 'Invalid html'}), 400
            # Sanitize filename and strip leading timestamp segments for a clean name
            safe = secure_filename(filename)
            stem = Path(safe).stem if safe else 'edited'
            parts = stem.split('_')
            while parts and parts[0].isdigit():
                parts.pop(0)
            base = '_'.join(parts) if parts else 'edited'
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"{timestamp}_{base}.docx"
            output_path = output_folder / output_filename
            html_to_docx(html, output_path)
            download_name = f"{base}.docx"
            return jsonify({
                'success': True,
                'download_url': f'/api/download/{output_filename}',
                'filename': download_name
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/health')
    def health_check():
        """Check API and dependencies status"""
        deps = {}
        for dep in ['pdfplumber', 'pytesseract', 'pdf2image', 'docx', 'pypdf', 'mammoth', 'bs4']:
            try:
                __import__(dep)
                deps[dep] = True
            except ImportError:
                deps[dep] = False

        return jsonify({
            'status': 'ok',
            'dependencies': deps
        })
