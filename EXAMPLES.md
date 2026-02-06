# PDF Converter - Usage Examples

## Scenario 1: Regulatory Compliance Review

**Problem:** Your team receives scanned regulatory documents that need to be reviewed and quoted in compliance reports.

**Solution:**
```bash
# Convert the scanned regulation PDF to Word document
python pdf_converter.py regulatory_document.pdf --format docx --dpi 400

# Result: regulatory_document_converted.docx
# Now you can search, copy-paste, and quote text easily
```

## Scenario 2: Batch Processing Old Archives

**Problem:** You have 50 scanned PDFs from 2010 that need to be digitized.

**Solution:**
```bash
#!/bin/bash
# batch_process.sh

mkdir -p converted_docs

for pdf in archive_2010/*.pdf; do
    echo "Processing: $pdf"
    python pdf_converter.py "$pdf" \
        --format docx \
        --dpi 300 \
        -o "converted_docs/$(basename "$pdf" .pdf).docx"
done

echo "All files converted!"
```

## Scenario 3: Multi-Language Documents

**Problem:** Processing French regulatory documents.

**Solution:**
```bash
# Install French language pack first
sudo apt-get install tesseract-ocr-fra

# Convert with French OCR
python pdf_converter.py french_regulation.pdf --lang fra --format docx
```

## Scenario 4: Quick Text Extraction

**Problem:** Need to quickly extract text from a PDF to send via email.

**Solution:**
```bash
# Convert to plain text
python pdf_converter.py document.pdf

# Copy the text
cat document_converted.txt | xclip -selection clipboard  # Linux
# or
cat document_converted.txt | pbcopy  # macOS
```

## Scenario 5: Quality vs Speed Trade-off

**Problem:** Large document that needs quick processing.

**Solution:**
```bash
# Fast processing (lower quality)
python pdf_converter.py large_doc.pdf --dpi 200

# High quality (slower)
python pdf_converter.py important_doc.pdf --dpi 400
```

## Scenario 6: Force OCR on Searchable PDFs

**Problem:** A PDF claims to be searchable but the text is garbled or incorrectly extracted.

**Solution:**
```bash
# Force OCR even though PDF has embedded text
python pdf_converter.py problematic.pdf --force-ocr --dpi 300
```

## Scenario 7: Web Interface for Non-Technical Users

**Problem:** Regulatory team members aren't comfortable with command line.

**Solution:**
```bash
# Start the web server
python app.py

# Share with team: "Go to http://<your-computer-ip>:5000"
# They can drag-and-drop files and download results
```

## Scenario 8: Integration with Document Management System

**Problem:** Need to automatically convert uploaded PDFs in your system.

**Solution:**
```python
# integration_example.py
from pdf_converter import PDFConverter
import os

def process_uploaded_pdf(pdf_path, output_dir):
    """
    Process uploaded PDF and save to output directory
    """
    try:
        converter = PDFConverter(pdf_path, 'docx')
        output_file = os.path.join(
            output_dir, 
            os.path.basename(pdf_path).replace('.pdf', '_converted.docx')
        )
        
        result = converter.convert(
            force_ocr=False,
            dpi=300,
            output_path=output_file
        )
        
        return {'success': True, 'file': result}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Usage
result = process_uploaded_pdf('/uploads/document.pdf', '/processed/')
```

## Scenario 9: Table Extraction (Advanced)

**Problem:** PDF contains important tables that need to be extracted.

**Solution:**
```python
# extract_tables.py
import pdfplumber
import pandas as pd

def extract_tables_from_pdf(pdf_path, output_excel):
    """
    Extract all tables from PDF and save to Excel
    """
    all_tables = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables()
            
            for table_num, table in enumerate(tables, 1):
                if table and len(table) > 1:
                    # Convert to DataFrame
                    df = pd.DataFrame(table[1:], columns=table[0])
                    df['source_page'] = page_num
                    df['table_number'] = table_num
                    all_tables.append(df)
    
    # Combine and save
    if all_tables:
        combined = pd.concat(all_tables, ignore_index=True)
        combined.to_excel(output_excel, index=False)
        print(f"Extracted {len(all_tables)} tables to {output_excel}")
    else:
        print("No tables found in PDF")

# Usage
extract_tables_from_pdf('financial_report.pdf', 'extracted_tables.xlsx')
```

## Scenario 10: Automated Compliance Workflow

**Problem:** Weekly regulatory documents need to be processed and distributed.

**Solution:**
```bash
#!/bin/bash
# weekly_compliance_workflow.sh

# Set up directories
INBOX="/path/to/inbox"
PROCESSED="/path/to/processed"
ARCHIVE="/path/to/archive"

# Create log file
LOG_FILE="conversion_log_$(date +%Y%m%d).txt"

echo "Starting weekly compliance document processing..." | tee -a $LOG_FILE
echo "Date: $(date)" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

# Process all PDFs in inbox
for pdf in "$INBOX"/*.pdf; do
    if [ -f "$pdf" ]; then
        filename=$(basename "$pdf")
        echo "Processing: $filename" | tee -a $LOG_FILE
        
        # Convert to DOCX
        python pdf_converter.py "$pdf" \
            --format docx \
            --dpi 300 \
            -o "$PROCESSED/${filename%.pdf}.docx" \
            2>&1 | tee -a $LOG_FILE
        
        # Move original to archive
        mv "$pdf" "$ARCHIVE/"
        
        echo "Completed: $filename" | tee -a $LOG_FILE
        echo "----------------------------------------" | tee -a $LOG_FILE
    fi
done

echo "" | tee -a $LOG_FILE
echo "Processing complete!" | tee -a $LOG_FILE

# Send notification email (optional)
# mail -s "Weekly Compliance Processing Complete" team@company.com < $LOG_FILE
```

## Performance Benchmarks

Based on typical regulatory documents:

| Document Type | Pages | DPI | Processing Time | Quality |
|--------------|-------|-----|-----------------|---------|
| Clear scan | 10 | 200 | ~30 seconds | Good |
| Clear scan | 10 | 300 | ~1 minute | Excellent |
| Clear scan | 10 | 400 | ~2 minutes | Superior |
| Poor scan | 10 | 300 | ~1.5 minutes | Good |
| Poor scan | 10 | 400 | ~3 minutes | Excellent |
| Digital PDF | 10 | N/A | ~5 seconds | Perfect |
| Large doc | 100 | 300 | ~10 minutes | Excellent |

## Tips for Best Results

1. **Pre-processing scans:**
   - Ensure scans are straight (not tilted)
   - Use adequate lighting/contrast
   - Scan at 300 DPI or higher

2. **Choose the right DPI:**
   - 200: Good for very clear documents, fast
   - 300: Standard, works for most documents
   - 400: Best for poor quality or small text

3. **Language selection:**
   - Always select the correct language
   - Install language packs beforehand
   - Can mix languages if needed

4. **Output format choice:**
   - TXT: Fastest, smallest files, good for pure text
   - DOCX: Better formatting, editable, good for reports

5. **Batch processing:**
   - Process during off-hours
   - Use standard DPI (300) for consistency
   - Keep logs for tracking

## Common Issues and Solutions

### Issue: "Tesseract not found"
```bash
# Solution: Install Tesseract
sudo apt-get install tesseract-ocr
```

### Issue: "PDF to image conversion failed"
```bash
# Solution: Install Poppler
sudo apt-get install poppler-utils
```

### Issue: Poor OCR quality
```bash
# Solution: Increase DPI and ensure good source quality
python pdf_converter.py doc.pdf --dpi 400
```

### Issue: Wrong language detected
```bash
# Solution: Specify language explicitly
python pdf_converter.py doc.pdf --lang fra
```

### Issue: Out of memory on large files
```bash
# Solution: Lower DPI or process pages in smaller batches
python pdf_converter.py large.pdf --dpi 200
```
