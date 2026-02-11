/**
 * Document editor - Word-like editing after DOCX conversion.
 * Loads DOCX as HTML, edits with TinyMCE, saves back as DOCX.
 */

(function () {
    const API_BASE = '';

    function getQueryParam(name) {
        const params = new URLSearchParams(window.location.search);
        return params.get(name);
    }

    function showLoading(show) {
        document.getElementById('editor-loading').style.display = show ? 'block' : 'none';
    }

    function showContainer(show) {
        const el = document.getElementById('editor-container');
        el.classList.toggle('editor-container-hidden', !show);
    }

    function showError(message) {
        const errEl = document.getElementById('editor-error');
        errEl.textContent = message;
        errEl.classList.remove('editor-error-hidden');
        document.getElementById('editor-container').classList.add('editor-container-hidden');
    }

    function setStatus(message, isError) {
        const el = document.getElementById('editor-status');
        el.textContent = message;
        el.className = isError ? 'status error' : '';
    }

    const file = getQueryParam('file');
    if (!file || !file.toLowerCase().endsWith('.docx')) {
        showError('Missing or invalid document. Convert to Word (.DOCX) first, then use "Proceed to edit".');
        showLoading(false);
        return;
    }

    // Send full server filename so backend can derive a clean save name

    showLoading(true);

    fetch(`${API_BASE}/api/document/${encodeURIComponent(file)}/html`)
        .then(function (res) {
            return res.json().then(function (data) {
                if (!res.ok) throw new Error(data.error || 'Failed to load document');
                return data;
            });
        })
        .then(function (data) {
            if (!data.success || data.html === undefined) {
                throw new Error(data.error || 'Invalid response');
            }
            showLoading(false);
            initEditor(data.html);
        })
        .catch(function (err) {
            showLoading(false);
            showError(err.message || 'Could not load document.');
        });

    function initEditor(initialHtml) {
        document.getElementById('editor-error').classList.add('editor-error-hidden');
        showContainer(true);

        tinymce.init({
            selector: '#editor',
            base_url: 'https://cdn.jsdelivr.net/npm/tinymce@6',
            suffix: '.min',
            promotion: false,
            branding: false,
            height: 580,
            menubar: false,
            plugins: 'lists link',
            toolbar: 'undo redo | blocks | bold italic underline | fontfamily fontsize forecolor | alignleft aligncenter alignright | bullist numlist | link',
            block_formats: 'Paragraph=p; Heading 1=h1; Heading 2=h2; Heading 3=h3',
            font_family_formats: [
                'Arial=arial,helvetica,sans-serif',
                'Arial Black=arial black,sans-serif',
                'Book Antiqua=book antiqua,palatino,serif',
                'Calibri=calibri,sans-serif',
                'Cambria=cambria,serif',
                'Century Gothic=century gothic,sans-serif',
                'Comic Sans MS=comic sans ms,cursive',
                'Courier New=courier new,courier,monospace',
                'Georgia=georgia,serif',
                'Helvetica=helvetica,arial,sans-serif',
                'Impact=impact,sans-serif',
                'Lucida Console=lucida console,monaco,monospace',
                'Lucida Sans Unicode=lucida sans unicode,lucida grande,sans-serif',
                'Palatino Linotype=palatino linotype,book antiqua,palatino,serif',
                'Tahoma=tahoma,geneva,sans-serif',
                'Times New Roman=times new roman,times,serif',
                'Trebuchet MS=trebuchet ms,helvetica,sans-serif',
                'Verdana=verdana,geneva,sans-serif'
            ].join('; '),
            font_size_formats: '8pt 10pt 11pt 12pt 14pt 18pt 24pt 36pt',
            content_style: 'body { font-family: Arial, sans-serif; font-size: 11pt; }',
            setup: function (ed) {
                ed.on('init', function () {
                    ed.setContent(initialHtml || '');
                });
            }
        });

        document.getElementById('btnSave').addEventListener('click', function () {
            const html = tinymce.get('editor') ? tinymce.get('editor').getContent() : '';
            setStatus('Saving…', false);

            fetch(`${API_BASE}/api/save-docx`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ html: html, filename: file })
            })
                .then(function (res) {
                    return res.json().then(function (data) {
                        if (!res.ok) throw new Error(data.error || 'Save failed');
                        return data;
                    });
                })
                .then(function (data) {
                    setStatus('Saved. Download your file below.', false);
                    const btn = document.getElementById('btnDownload');
                    btn.href = API_BASE + data.download_url;
                    btn.download = data.filename || 'document.docx';
                    btn.classList.remove('btn-download-hidden');
                })
                .catch(function (err) {
                    setStatus(err.message || 'Save failed', true);
                });
        });
    }
})();
