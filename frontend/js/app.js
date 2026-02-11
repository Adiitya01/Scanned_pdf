/**
 * PDF Converter - Frontend Application
 * Handles file upload, API calls, and UI state
 */

const API_BASE = '';  // Same origin

const elements = {
    uploadZone: document.getElementById('uploadZone'),
    fileInput: document.getElementById('fileInput'),
    filePreview: document.getElementById('filePreview'),
    fileName: document.getElementById('fileName'),
    fileSize: document.getElementById('fileSize'),
    btnClear: document.getElementById('btnClear'),
    optionsSection: document.getElementById('optionsSection'),
    format: document.getElementById('format'),
    dpi: document.getElementById('dpi'),
    lang: document.getElementById('lang'),
    forceOcr: document.getElementById('forceOcr'),
    preserveColor: document.getElementById('preserveColor'),
    btnConvert: document.getElementById('btnConvert'),
    btnDownload: document.getElementById('btnDownload'),
    btnEdit: document.getElementById('btnEdit'),
    status: document.getElementById('status'),
    progress: document.getElementById('progress'),
};

let selectedFile = null;
let downloadUrl = null;
let editUrl = null;

// Upload zone click
elements.uploadZone.addEventListener('click', () => elements.fileInput.click());

// Drag and drop
elements.uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    elements.uploadZone.classList.add('dragover');
});

elements.uploadZone.addEventListener('dragleave', () => {
    elements.uploadZone.classList.remove('dragover');
});

elements.uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    elements.uploadZone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].type === 'application/pdf') {
        handleFile(files[0]);
    } else {
        showStatus('Please drop a PDF file', 'error');
    }
});

// File input change
elements.fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

// Clear file
elements.btnClear.addEventListener('click', (e) => {
    e.stopPropagation();
    clearFile();
});

// Convert button
elements.btnConvert.addEventListener('click', convertFile);

// Download button
elements.btnDownload.addEventListener('click', () => {
    if (downloadUrl) {
        window.location.href = downloadUrl;
    }
});

// Proceed to edit (opens editor for DOCX)
elements.btnEdit.addEventListener('click', (e) => {
    if (editUrl) {
        window.location.href = editUrl;
    } else {
        e.preventDefault();
    }
});

function handleFile(file) {
    selectedFile = file;
    elements.fileName.textContent = file.name;
    elements.fileSize.textContent = formatFileSize(file.size);
    elements.uploadZone.style.display = 'none';
    elements.filePreview.hidden = false;
    elements.optionsSection.hidden = false;
    elements.btnConvert.disabled = false;
    elements.btnConvert.textContent = 'Convert';
    elements.btnDownload.hidden = true;
    elements.btnEdit.hidden = true;
    editUrl = null;
    hideStatus();
}

function clearFile() {
    selectedFile = null;
    downloadUrl = null;
    editUrl = null;
    elements.fileInput.value = '';
    elements.uploadZone.style.display = 'block';
    elements.filePreview.hidden = true;
    elements.optionsSection.hidden = true;
    elements.btnConvert.disabled = true;
    elements.btnDownload.hidden = true;
    elements.btnEdit.hidden = true;
    hideStatus();
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return ` • ${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
}

function showStatus(message, type = 'info') {
    elements.status.textContent = message;
    elements.status.className = `status ${type}`;
    elements.status.hidden = false;
}

function hideStatus() {
    elements.status.hidden = true;
}

async function convertFile() {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('format', elements.format.value);
    formData.append('dpi', elements.dpi.value);
    formData.append('lang', elements.lang.value);
    formData.append('force_ocr', elements.forceOcr.checked);
    formData.append('preserve_color', elements.preserveColor.checked);

    // UI state
    elements.btnConvert.disabled = true;
    elements.btnConvert.textContent = 'Converting…';
    elements.progress.hidden = false;
    elements.btnDownload.hidden = true;
    showStatus('Processing your PDF. This may take a minute.', 'info');

    try {
        const response = await fetch(`${API_BASE}/api/convert`, {
            method: 'POST',
            body: formData,
        });

        let result;
        try {
            const text = await response.text();
            result = text ? JSON.parse(text) : {};
        } catch (_) {
            showStatus('Server returned invalid response', 'error');
            elements.btnConvert.disabled = false;
            elements.btnConvert.textContent = 'Try again';
            elements.progress.hidden = true;
            return;
        }

        if (response.ok && result.success) {
            downloadUrl = result.download_url;
            editUrl = result.edit_url || null;
            showStatus('Conversion complete! Click Download' + (editUrl ? ' or Proceed to edit.' : '.'), 'success');
            elements.btnDownload.hidden = false;
            if (editUrl) {
                elements.btnEdit.href = editUrl;
                elements.btnEdit.hidden = false;
            } else {
                elements.btnEdit.hidden = true;
            }
            elements.btnConvert.textContent = 'Convert another';
        } else {
            showStatus(result.error || 'Conversion failed', 'error');
            elements.btnConvert.disabled = false;
            elements.btnConvert.textContent = 'Try again';
        }
    } catch (err) {
        showStatus(err.message || 'Network error', 'error');
        elements.btnConvert.disabled = false;
        elements.btnConvert.textContent = 'Try again';
    } finally {
        elements.progress.hidden = true;
    }
}
