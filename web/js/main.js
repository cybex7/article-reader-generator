/**
 * اتصال فرم ورودی به پارسرها و قالب، و مدیریت پیش‌نمایش زنده / دانلود فایل مستقل.
 */

(function () {
  const titleInput = document.querySelector('input[name="title"]');
  const authorInput = document.querySelector('input[name="author"]');
  const dateInput = document.querySelector('input[name="date"]');
  const contentArea = document.getElementById('content-area');
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const formSection = document.getElementById('form-section');
  const previewSection = document.getElementById('preview-section');
  const previewFrame = document.getElementById('preview-frame');
  const articleForm = document.getElementById('article-form');
  const backBtn = document.getElementById('back-btn');
  const downloadBtn = document.getElementById('download-btn');
  const formatButtons = {
    plain: document.getElementById('format-plain-btn'),
    markdown: document.getElementById('format-markdown-btn'),
  };
  const formatInput = document.getElementById('format-value');

  let lastGeneratedHtml = '';

  function setFormat(format) {
    formatInput.value = format;
    Object.entries(formatButtons).forEach(([key, btn]) => {
      if (!btn) return;
      btn.className = key === format
        ? 'px-3 py-1.5 rounded-lg transition bg-blue-600 text-white font-semibold shadow-xs text-xs'
        : 'px-3 py-1.5 rounded-lg transition text-gray-600 text-xs';
    });
  }

  formatButtons.plain.addEventListener('click', () => setFormat('plain'));
  formatButtons.markdown.addEventListener('click', () => setFormat('markdown'));
  setFormat('markdown');

  function loadFile(file) {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      contentArea.value = reader.result;
      if (!titleInput.value) {
        titleInput.value = file.name.replace(/\.[^/.]+$/, '').replace(/[_-]+/g, ' ');
      }
      const isMarkdown = /\.(md|markdown)$/i.test(file.name);
      setFormat(isMarkdown ? 'markdown' : 'plain');
    };
    reader.readAsText(file, 'utf-8');
  }

  dropzone.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', (e) => loadFile(e.target.files[0]));

  ['dragenter', 'dragover'].forEach((evt) =>
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.add('drag-over');
    })
  );
  ['dragleave', 'drop'].forEach((evt) =>
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.remove('drag-over');
    })
  );
  dropzone.addEventListener('drop', (e) => loadFile(e.dataTransfer.files[0]));

  function slugifyFilename(title) {
    const trimmed = (title || 'article').trim();
    return trimmed.length ? trimmed.replace(/\s+/g, '_') : 'article';
  }

  articleForm.addEventListener('submit', (e) => {
    e.preventDefault();

    const format = formatInput.value;
    const rawContent = contentArea.value;
    if (!rawContent.trim()) {
      contentArea.focus();
      return;
    }

    const parsed = format === 'markdown'
      ? parseMarkdownArticle(rawContent)
      : parsePlainArticle(rawContent);

    const title = titleInput.value || 'بدون عنوان';
    lastGeneratedHtml = buildArticleHtml({
      title,
      subtitle: '',
      author: authorInput.value,
      date: dateInput.value,
      contentHtml: parsed.contentHtml,
      readTime: parsed.readTime,
      toc: parsed.toc,
      format,
    });

    previewFrame.srcdoc = lastGeneratedHtml;
    formSection.classList.add('hidden');
    previewSection.classList.remove('hidden');
  });

  backBtn.addEventListener('click', () => {
    previewSection.classList.add('hidden');
    formSection.classList.remove('hidden');
  });

  downloadBtn.addEventListener('click', () => {
    if (!lastGeneratedHtml) return;
    const blob = new Blob([lastGeneratedHtml], { type: 'text/html;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${slugifyFilename(titleInput.value)}.html`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  });
})();
