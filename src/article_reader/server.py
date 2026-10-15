"""رابط وب مینیمال برای چسباندن یا آپلود متن مقاله و دریافت خروجی HTML."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs

from .markdown_parser import MarkdownArticleParser
from .parser import ArticleParser
from .template import ReaderHTMLTemplate
from .url_import import UrlFetchError, fetch_article

INDEX_HTML = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>سامانه تولید صفحات مطالعه ارگونومیک</title>
  <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;600;700&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body { font-family: 'Vazirmatn', sans-serif; }
    #dropzone.drag-over { background-color: #eff6ff; border-color: #2563eb; }
  </style>
</head>
<body class="bg-gray-50 text-gray-800 min-h-screen p-6">
  <div class="max-w-3xl mx-auto bg-white p-8 rounded-2xl shadow-sm border border-gray-200">
    <h1 class="text-2xl font-bold mb-2 text-blue-900">مبدل هوشمند مقاله به صفحه مطالعه</h1>
    <p class="text-sm text-gray-500 mb-6">متن خود را وارد کنید یا فایل TXT/MD را بکشید و رها کنید تا نسخه استاندارد و خوانا با تم‌های مطالعه تولید شود.</p>

    <form method="POST" action="/generate" class="space-y-4">
      <div>
        <label class="block text-xs font-bold mb-1">عنوان مقاله</label>
        <input type="text" name="title" required placeholder="مثال: مبانی جامعه‌شناسی" class="w-full border rounded-xl p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500">
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-xs font-bold mb-1">نویسنده / ارائه‌دهنده</label>
          <input type="text" name="author" placeholder="مثال: امین بزرگیان" class="w-full border rounded-xl p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500">
        </div>
        <div>
          <label class="block text-xs font-bold mb-1">تاریخ یا جلسه</label>
          <input type="text" name="date" placeholder="مثال: جلسه اول - ۰۵/۰۵/۲۱" class="w-full border rounded-xl p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500">
        </div>
      </div>

      <div>
        <label class="block text-xs font-bold mb-1">یا دریافت خودکار از آدرس یک صفحه وب</label>
        <div class="flex gap-2">
          <input type="url" id="url-input" placeholder="https://example.com/article" class="flex-1 border rounded-xl p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" dir="ltr">
          <button type="button" id="fetch-url-btn" class="px-4 rounded-xl bg-gray-800 hover:bg-gray-900 text-white text-sm font-bold transition shrink-0">
            دریافت متن
          </button>
        </div>
        <p id="url-status" class="text-xs text-gray-500 mt-1"></p>
      </div>

      <div id="dropzone" class="border-2 border-dashed border-gray-300 rounded-xl p-4 text-center text-xs text-gray-500 transition-colors cursor-pointer">
        📄 فایل TXT یا MD را اینجا بکشید و رها کنید، یا <span class="text-blue-600 font-bold">کلیک کنید</span>
        <input type="file" id="file-input" accept=".txt,.md,.markdown,text/plain,text/markdown" class="hidden">
      </div>

      <div class="flex items-center justify-between">
        <label class="block text-xs font-bold">نوع محتوا</label>
        <div class="flex items-center border border-gray-200 rounded-lg p-0.5 bg-gray-50">
          <button type="button" id="format-plain-btn" class="px-3 py-1.5 rounded-lg transition text-gray-600 text-xs">یادداشت ساده</button>
          <button type="button" id="format-markdown-btn" class="px-3 py-1.5 rounded-lg transition bg-blue-600 text-white font-semibold shadow-xs text-xs">مارک‌داون کامل</button>
        </div>
        <input type="hidden" name="format" id="format-value" value="markdown">
      </div>

      <div>
        <label class="block text-xs font-bold mb-1">متن اصلی مقاله</label>
        <textarea name="content" id="content-area" rows="12" required placeholder="متن کامل یا یادداشت‌ها را اینجا بچسبانید..." class="w-full border rounded-xl p-3 text-sm leading-relaxed outline-none focus:ring-2 focus:ring-blue-500"></textarea>
      </div>
      <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl transition shadow-sm">
        تولید و دانلود صفحه مطالعه (HTML)
      </button>
    </form>
  </div>

  <script>
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const contentArea = document.getElementById('content-area');
    const titleInput = document.querySelector('input[name="title"]');
    const formatInput = document.getElementById('format-value');
    const formatButtons = {
      plain: document.getElementById('format-plain-btn'),
      markdown: document.getElementById('format-markdown-btn'),
    };

    function setFormat(fmt) {
      formatInput.value = fmt;
      Object.entries(formatButtons).forEach(([key, btn]) => {
        btn.className = key === fmt
          ? 'px-3 py-1.5 rounded-lg transition bg-blue-600 text-white font-semibold shadow-xs text-xs'
          : 'px-3 py-1.5 rounded-lg transition text-gray-600 text-xs';
      });
    }

    formatButtons.plain.addEventListener('click', () => setFormat('plain'));
    formatButtons.markdown.addEventListener('click', () => setFormat('markdown'));

    function loadFile(file) {
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => {
        contentArea.value = reader.result;
        if (!titleInput.value) {
          titleInput.value = file.name.replace(/\\.[^/.]+$/, '').replace(/[_-]+/g, ' ');
        }
        setFormat(/\\.(md|markdown)$/i.test(file.name) ? 'markdown' : 'plain');
      };
      reader.readAsText(file, 'utf-8');
    }

    dropzone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => loadFile(e.target.files[0]));

    ['dragenter', 'dragover'].forEach(evt =>
      dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        dropzone.classList.add('drag-over');
      })
    );
    ['dragleave', 'drop'].forEach(evt =>
      dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        dropzone.classList.remove('drag-over');
      })
    );
    dropzone.addEventListener('drop', (e) => loadFile(e.dataTransfer.files[0]));

    const urlInput = document.getElementById('url-input');
    const fetchUrlBtn = document.getElementById('fetch-url-btn');
    const urlStatus = document.getElementById('url-status');
    const authorInput = document.querySelector('input[name="author"]');
    const dateInput = document.querySelector('input[name="date"]');

    fetchUrlBtn.addEventListener('click', async () => {
      const url = urlInput.value.trim();
      if (!url) return;

      fetchUrlBtn.disabled = true;
      urlStatus.textContent = 'در حال دریافت و استخراج متن...';
      urlStatus.className = 'text-xs text-gray-500 mt-1';

      try {
        const response = await fetch('/fetch-url', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: 'url=' + encodeURIComponent(url),
        });
        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || 'خطای نامشخص');
        }

        contentArea.value = data.content;
        if (!titleInput.value) titleInput.value = data.title;
        if (!authorInput.value) authorInput.value = data.author;
        if (!dateInput.value) dateInput.value = data.date;
        setFormat('markdown');

        urlStatus.textContent = '✓ متن با موفقیت دریافت شد؛ می‌توانید ویرایش کنید و سپس تولید بزنید.';
        urlStatus.className = 'text-xs text-green-600 mt-1';
      } catch (err) {
        urlStatus.textContent = '✗ ' + err.message;
        urlStatus.className = 'text-xs text-red-600 mt-1';
      } finally {
        fetchUrlBtn.disabled = false;
      }
    });
  </script>
</body>
</html>"""


class ArticleReaderRequestHandler(BaseHTTPRequestHandler):
    """رابط وب مینیمال برای چسباندن متن مقاله و دریافت خروجی زنده"""

    def log_message(self, format: str, *args) -> None:  # noqa: A002 - imposed by base class
        pass

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(INDEX_HTML.encode('utf-8'))
        else:
            self.send_error(404)

    def do_POST(self) -> None:
        if self.path == "/fetch-url":
            self._handle_fetch_url()
            return
        if self.path != "/generate":
            self.send_error(404)
            return

        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        parsed_data = parse_qs(post_data)

        title = parsed_data.get('title', ['بدون عنوان'])[0]
        author = parsed_data.get('author', [''])[0]
        date = parsed_data.get('date', [''])[0]
        raw_content = parsed_data.get('content', [''])[0]
        content_format = parsed_data.get('format', ['plain'])[0]

        parser_cls = MarkdownArticleParser if content_format == 'markdown' else ArticleParser
        article = parser_cls.parse(raw_content)
        rendered_page = ReaderHTMLTemplate.render(
            title=title,
            subtitle="",
            author=author,
            date=date,
            content_html=article.content_html,
            read_time=article.read_time,
            toc=article.toc,
            format=content_format,
        )

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Disposition", 'attachment; filename="article.html"')
        self.end_headers()
        self.wfile.write(rendered_page.encode('utf-8'))

    def _handle_fetch_url(self) -> None:
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        parsed_data = parse_qs(post_data)
        url = parsed_data.get('url', [''])[0].strip()

        if not url:
            self._send_json(400, {"error": "آدرسی وارد نشده است."})
            return

        try:
            fetched = fetch_article(url)
        except UrlFetchError as e:
            self._send_json(400, {"error": str(e)})
            return
        except Exception:
            self._send_json(400, {"error": "خطایی هنگام دریافت یا پردازش این آدرس رخ داد."})
            return

        self._send_json(200, {
            "title": fetched.title,
            "author": fetched.author,
            "date": fetched.date,
            "content": fetched.content,
        })

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


# نام قدیمی برای سازگاری با کد قبلی
EmbeddedWebServer = ArticleReaderRequestHandler
