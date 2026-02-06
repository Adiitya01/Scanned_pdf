# PDF Converter Tool for Regulatory Teams

A comprehensive solution for converting non-readable PDFs (scanned documents, image-based PDFs) into readable, copy-pasteable formats. Designed specifically for regulatory teams who need to extract text from documents for compliance work.

## Features

✅ **Automatic Detection** - Automatically detects if a PDF is scanned or digital  
✅ **OCR Support** - Converts scanned PDFs to text using Tesseract OCR  
✅ **Multiple Output Formats** - Export to TXT or DOCX  
✅ **Multi-language Support** - Supports English, French, German, Spanish, Italian, Portuguese, Russian, Chinese, Japanese, Korean  
✅ **Quality Options** - Adjustable DPI for OCR quality (200-400 DPI)  
✅ **Web Interface** - Easy-to-use drag-and-drop web interface  
✅ **Command Line Tool** - Batch processing via CLI  
✅ **Preserves Page Structure** - Maintains page breaks and formatting  

## Installation

### Prerequisites

1. **Python 3.8+**
2. **System Dependencies**

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    python3-pip
```

#### macOS:
```bash
brew install tesseract
brew install poppler
```

#### Windows:
- Download and install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
- Download and install Poppler from: https://github.com/oschwartz10612/poppler-windows/releases

### Python Dependencies

```bash
pip install -r requirements.txt --break-system-packages
```

Or manually:
```bash
pip install pypdf pdfplumber pytesseract pdf2image Pillow python-docx Flask --break-system-packages
```

### Additional Language Support (Optional)

For OCR in languages other than English:

```bash
# French
sudo apt-get install tesseract-ocr-fra

# German
sudo apt-get install tesseract-ocr-deu

# Spanish
sudo apt-get install tesseract-ocr-spa

# All languages
sudo apt-get install tesseract-ocr-all
```

## Usage

### Option 1: Web Interface (Recommended)

1. **Start the web server:**
```bash
python app.py
```

2. **Open your browser:**
```
http://localhost:5000
```

3. **Upload and convert:**
   - Drag and drop your PDF or click to browse
   - Select output format (TXT or DOCX)
   - Choose OCR quality
   - Click "Convert PDF"
   - Download your converted file

### Option 2: Command Line Tool

#### Basic Usage:
```bash
# Convert scanned PDF to text
python pdf_converter.py document.pdf

# Convert to Word document
python pdf_converter.py document.pdf --format docx

# Specify output file
python pdf_converter.py document.pdf -o output.txt
```

#### Advanced Options:
```bash
# Force OCR even if PDF has selectable text
python pdf_converter.py document.pdf --force-ocr

# Use high-quality OCR (400 DPI)
python pdf_converter.py document.pdf --dpi 400

# OCR with French language
python pdf_converter.py document.pdf --lang fra

# Combine options
python pdf_converter.py document.pdf --format docx --dpi 400 --lang fra -o report.docx
```

#### Command Line Help:
```bash
python pdf_converter.py --help
```

## How It Works

### 1. PDF Type Detection
The tool automatically analyzes the first few pages to determine if the PDF contains selectable text or if it's a scanned image.

### 2. Text Extraction
- **Digital PDFs**: Direct text extraction using pdfplumber
- **Scanned PDFs**: OCR processing using Tesseract

### 3. Output Generation
- **TXT**: Plain text with page markers
- **DOCX**: Formatted Word document with page headings

## Batch Processing Example

Process multiple PDFs at once:

```bash
#!/bin/bash
# batch_convert.sh

for pdf in *.pdf; do
    echo "Converting: $pdf"
    python pdf_converter.py "$pdf" --format docx
done
```

## Architecture

```
pdf_converter/
├── app.py                  # Flask web application
├── pdf_converter.py        # Core conversion logic
├── templates/
│   └── index.html         # Web interface
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Use Cases

### Regulatory Compliance
- Extract text from scanned regulations and policies
- Convert legacy documents to searchable formats
- Prepare documents for compliance reviews

### Document Management
- Digitize paper archives
- Make old scanned PDFs searchable
- Extract data from invoices and forms

### Legal Documents
- Convert court filings to editable text
- Extract clauses from scanned contracts
- Prepare documents for legal review

## Troubleshooting

### OCR not working?
```bash
# Verify Tesseract installation
tesseract --version

# Test Tesseract
tesseract test_image.png output -l eng
```

### PDF to image conversion failing?
```bash
# Verify Poppler installation
pdftoppm -v
```

### Permission errors on Linux?
```bash
# Use --break-system-packages flag
pip install <package> --break-system-packages
```

### Poor OCR quality?
- Increase DPI (try 400 or higher)
- Ensure the source PDF is high resolution
- Check if the correct language is selected

### Large file processing slow?
- Lower DPI to 200 for faster processing
- Process files in smaller batches
- Use the command line tool for better performance

## Performance Tips

1. **DPI Settings**:
   - 200 DPI: Fast, good for clear documents
   - 300 DPI: Standard, balance of speed and quality
   - 400 DPI: Slow, best quality for difficult documents

2. **Batch Processing**:
   - Use command line for multiple files
   - Process overnight for large batches

3. **System Resources**:
   - OCR is CPU-intensive
   - More RAM helps with large PDFs
   - SSD speeds up processing

## Security Considerations

- Files are temporarily stored during processing
- Files are automatically cleaned up after 24 hours
- For production use:
  - Change the Flask secret key in `app.py`
  - Use HTTPS
  - Implement user authentication
  - Add virus scanning for uploads
  - Set up proper file permissions

## Deployment Options

### Local Server
Run on a local machine for team access:
```bash
python app.py
# Access from other computers: http://<your-ip>:5000
```

### Docker (Optional)
Create a Dockerfile for containerized deployment:
```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-all \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "app.py"]
```

### Production Server
For production deployment:
- Use Gunicorn or uWSGI
- Set up Nginx as reverse proxy
- Enable SSL/TLS
- Implement rate limiting
- Add logging and monitoring

## API Documentation

### POST /convert

Convert a PDF file.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Parameters:
  - `file`: PDF file (required)
  - `format`: 'txt' or 'docx' (optional, default: 'txt')
  - `force_ocr`: 'true' or 'false' (optional)
  - `dpi`: 200-400 (optional, default: 300)
  - `lang`: language code (optional, default: 'eng')

**Response:**
```json
{
  "success": true,
  "download_url": "/download/filename.txt",
  "filename": "document_converted.txt"
}
```

### GET /download/<filename>

Download the converted file.

### GET /health

Check service health and dependencies.

## License

This tool uses open-source libraries:
- pypdf (BSD License)
- pdfplumber (MIT License)
- pytesseract (Apache License 2.0)
- Tesseract OCR (Apache License 2.0)
- Flask (BSD License)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all dependencies are installed
3. Test with a simple PDF first
4. Check system resources (CPU, RAM, disk space)

## Future Enhancements

Potential improvements:
- [ ] Support for more output formats (HTML, Markdown)
- [ ] Table extraction and preservation
- [ ] Image extraction
- [ ] PDF merging and splitting
- [ ] Cloud storage integration (Google Drive, Dropbox)
- [ ] Email notification when processing completes
- [ ] REST API for integration with other systems
- [ ] User authentication and file history
- [ ] Improved error handling and logging
- [ ] Progress indicators for long-running conversions

## Contributing

Contributions are welcome! Areas for improvement:
- Better OCR accuracy
- Additional output formats
- UI/UX enhancements
- Performance optimizations
- Better error handling
- More language support

## Changelog

### Version 1.0.0
- Initial release
- Web interface with drag-and-drop
- Command line tool
- OCR support for scanned PDFs
- TXT and DOCX output formats
- Multi-language support
- Automatic PDF type detection
