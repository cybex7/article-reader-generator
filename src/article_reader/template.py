"""قالب اصلی تولید سند HTML مستقل و بهینه برای صفحه مطالعه."""

from __future__ import annotations

import html

from .parser import TocEntry


def _render_toc(toc: list[TocEntry]) -> str:
    """فهرست مطالب را در صورت وجود بیش از یک بخش می‌سازد"""
    if len(toc) < 2:
        return ""

    items = "\n".join(
        f'<li style="padding-right:{max(0, entry.level - 1) * 0.9}rem">'
        f'<a href="#{entry.anchor_id}" '
        f'class="block py-1.5 px-2 rounded-lg hover:bg-blue-50 dark:hover:bg-zinc-800 '
        f'text-gray-700 dark:text-zinc-300 hover:text-blue-700 dark:hover:text-blue-300 transition">'
        f'{entry.title}</a></li>'
        for entry in toc
    )

    return f"""
    <details class="card-box border rounded-2xl mb-8 open:pb-2" open>
      <summary class="cursor-pointer select-none px-4 sm:px-5 py-3 font-bold text-sm text-gray-900 dark:text-white flex items-center gap-2">
        📑 فهرست مطالب
      </summary>
      <ul class="px-3 sm:px-4 pb-2 text-sm space-y-0.5">
        {items}
      </ul>
    </details>
    """


class ReaderHTMLTemplate:
    """قالب اصلی تولید سند HTML مستقل و بهینه"""

    @staticmethod
    def render(
        title: str,
        subtitle: str,
        author: str,
        date: str,
        content_html: str,
        read_time: int,
        toc: list[TocEntry] | None = None,
        format: str = "plain",
    ) -> str:
        toc_html = _render_toc(toc or [])
        body_html = f'<div class="markdown-body">{content_html}</div>' if format == "markdown" else content_html
        return f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)}</title>

  <!-- فونت استاندارد وزیرمتن -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          fontFamily: {{
            vazir: ['Vazirmatn', 'Tahoma', 'sans-serif'],
          }},
          colors: {{
            sepia: {{
              bg: '#fbf7ee',
              card: '#f4ede0',
              text: '#382c1e',
              muted: '#7b6c59',
              border: '#e6dac7',
            }}
          }}
        }}
      }}
    }}
  </script>

  <style>
    html {{
      scroll-behavior: smooth;
    }}

    /* اصول بهینه خوانایی فارسی */
    body {{
      font-family: 'Vazirmatn', Tahoma, sans-serif;
      text-rendering: optimizeLegibility;
      -webkit-font-smoothing: antialiased;
      word-spacing: -0.5px;
    }}

    /* خطوط استاندارد مطالعه: ۶۰ تا ۷۵ نویسه در هر خط */
    .article-prose {{
      line-height: var(--article-line-height, 2.18);
      font-size: var(--article-font-size, 1rem); /* 1rem = 16px با فونت پایه پیش‌فرض مرورگر */
    }}

    .article-prose p {{
      margin-bottom: 1.6rem;
      text-align: justify;
      text-justify: inter-word;
    }}

    /* استایل‌های تم سه‌گانه */
    body.theme-light {{
      background-color: #fafafc;
      color: #27272a;
    }}
    body.theme-sepia {{
      background-color: #fbf7ee;
      color: #382c1e;
    }}
    body.theme-dark {{
      background-color: #121418;
      color: #e4e4e7;
    }}

    .theme-light .card-box {{
      background-color: #ffffff;
      border-color: #e5e7eb;
    }}
    .theme-sepia .card-box {{
      background-color: #f4ece0;
      border-color: #e2d5c3;
    }}
    .theme-dark .card-box {{
      background-color: #1a1d24;
      border-color: #2a2f3a;
    }}

    /* استایل عناصر خام تولیدشده توسط پارسر Markdown کامل */
    .markdown-body h1 {{ font-size: 1.75rem; font-weight: 800; margin-top: 2rem; margin-bottom: 1rem; }}
    .markdown-body h2 {{ font-size: 1.375rem; font-weight: 700; margin-top: 1.75rem; margin-bottom: 0.875rem; }}
    .markdown-body h3 {{ font-size: 1.125rem; font-weight: 700; margin-top: 1.5rem; margin-bottom: 0.75rem; }}
    .markdown-body h4 {{ font-size: 1rem; font-weight: 700; margin-top: 1.25rem; margin-bottom: 0.5rem; }}
    .markdown-body ul {{ list-style: disc; padding-right: 1.25rem; margin-bottom: 1.25rem; }}
    .markdown-body ol {{ list-style: decimal; padding-right: 1.25rem; margin-bottom: 1.25rem; }}
    .markdown-body li {{ margin-bottom: 0.4rem; }}
    .markdown-body li > ul, .markdown-body li > ol {{ margin-top: 0.4rem; margin-bottom: 0; }}
    .markdown-body a {{ color: #2563eb; text-decoration: underline; text-underline-offset: 2px; }}
    .markdown-body img {{ max-width: 100%; border-radius: 0.75rem; margin: 1.5rem auto; display: block; }}
    .markdown-body hr {{ border: none; border-top: 1px solid currentColor; opacity: 0.2; margin: 2.5rem 0; }}
    .markdown-body code {{
      font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
      font-size: 0.85em; padding: 0.15em 0.4em; border-radius: 0.35rem;
      background: rgba(127,127,127,0.15);
    }}
    .markdown-body pre {{
      padding: 1rem 1.25rem; border-radius: 0.9rem; overflow-x: auto; margin: 1.5rem 0;
      background: rgba(127,127,127,0.12);
    }}
    .markdown-body pre code {{ background: none; padding: 0; font-size: 0.85em; }}
    .markdown-body table {{ border: 1px solid rgba(127,127,127,0.25); }}
    .markdown-body th, .markdown-body td {{ border: 1px solid rgba(127,127,127,0.25); padding: 0.5rem 0.75rem; text-align: right; }}
    .markdown-body th {{ background: rgba(127,127,127,0.12); font-weight: 700; }}
    .markdown-body strong {{ font-weight: 700; }}

    @media print {{
      header, #progress-container, footer button {{
        display: none !important;
      }}
      body {{
        background-color: #fff !important;
        color: #000 !important;
      }}
    }}
  </style>
</head>
<body class="theme-light min-h-screen transition-colors duration-200">

  <!-- نوار پیشرفت مطالعه در بالای صفحه -->
  <div id="progress-container" class="fixed top-0 left-0 right-0 h-1.5 bg-transparent z-50">
    <div id="progress-bar" class="h-full bg-blue-600 dark:bg-blue-400 transition-all duration-75 w-0"></div>
  </div>

  <!-- نوار ابزار هدر (تغییر تم، اندازه قلم و زمان مطالعه) -->
  <header class="sticky top-0 z-40 backdrop-blur-md bg-white/85 dark:bg-[#121418]/85 border-b border-gray-200 dark:border-zinc-800 transition-colors">
    <div class="max-w-[760px] mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">

      <div class="flex items-center space-x-reverse space-x-2 text-xs sm:text-sm">
        <span class="font-bold text-gray-900 dark:text-zinc-100 truncate max-w-[200px] sm:max-w-xs">{html.escape(title)}</span>
      </div>

      <div class="flex items-center space-x-reverse space-x-2 overflow-x-auto">
        <!-- دکمه‌های کنترل اندازه فونت -->
        <div class="flex items-center shrink-0 border border-gray-200 dark:border-zinc-700 rounded-lg overflow-hidden p-0.5 bg-gray-50 dark:bg-zinc-800/60">
          <button onclick="changeFontSize(-1)" title="کوچک‌تر کردن متن" class="px-2.5 py-1 text-xs font-bold hover:bg-white dark:hover:bg-zinc-700 rounded transition text-gray-700 dark:text-zinc-300">
            A-
          </button>
          <button onclick="resetFontSize()" title="اندازه پیش‌فرض" class="px-2 py-1 text-xs hover:bg-white dark:hover:bg-zinc-700 rounded transition text-gray-500 dark:text-zinc-400">
            ۱۰۰٪
          </button>
          <button onclick="changeFontSize(1)" title="بزرگ‌تر کردن متن" class="px-2.5 py-1 text-xs font-bold hover:bg-white dark:hover:bg-zinc-700 rounded transition text-gray-700 dark:text-zinc-300">
            A+
          </button>
        </div>

        <!-- دکمه‌های کنترل فاصله خطوط -->
        <div class="flex items-center shrink-0 border border-gray-200 dark:border-zinc-700 rounded-lg overflow-hidden p-0.5 bg-gray-50 dark:bg-zinc-800/60">
          <button onclick="changeLineHeight(-1)" title="کاهش فاصله خطوط" class="px-2.5 py-1 text-xs font-bold hover:bg-white dark:hover:bg-zinc-700 rounded transition text-gray-700 dark:text-zinc-300">
            ↕-
          </button>
          <button onclick="resetLineHeight()" title="فاصله خط پیش‌فرض" class="px-2 py-1 text-xs hover:bg-white dark:hover:bg-zinc-700 rounded transition text-gray-500 dark:text-zinc-400">
            خط
          </button>
          <button onclick="changeLineHeight(1)" title="افزایش فاصله خطوط" class="px-2.5 py-1 text-xs font-bold hover:bg-white dark:hover:bg-zinc-700 rounded transition text-gray-700 dark:text-zinc-300">
            ↕+
          </button>
        </div>

        <!-- انتخاب حالت تم -->
        <div class="flex items-center shrink-0 border border-gray-200 dark:border-zinc-700 rounded-lg p-0.5 bg-gray-50 dark:bg-zinc-800/60 text-xs">
          <button onclick="setTheme('auto')" id="btn-auto" title="پیروی از تنظیم سیستم" class="px-2 py-1 rounded transition text-gray-600">
            خودکار
          </button>
          <button onclick="setTheme('light')" id="btn-light" class="px-2 py-1 rounded transition text-gray-600">
            روشن
          </button>
          <button onclick="setTheme('sepia')" id="btn-sepia" class="px-2 py-1 rounded transition text-gray-600">
            سپیا
          </button>
          <button onclick="setTheme('dark')" id="btn-dark" class="px-2 py-1 rounded transition text-gray-600">
            شب
          </button>
        </div>
      </div>

    </div>
  </header>

  <!-- ستون اصلی مقاله با عرض استاندارد مطالعه -->
  <main class="max-w-[740px] mx-auto px-5 sm:px-8 pt-10 pb-24">

    <!-- سربرگ مقاله -->
    <header class="mb-10 pb-6 border-b border-gray-200 dark:border-zinc-800">
      <div class="flex flex-wrap items-center gap-2 text-xs font-medium text-blue-600 dark:text-blue-400 mb-3">
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full bg-blue-100/70 dark:bg-zinc-800 text-blue-800 dark:text-blue-300">⏱ {read_time} دقیقه مطالعه</span>
        {f'<span>•</span><span>{html.escape(author)}</span>' if author else ''}
        {f'<span>•</span><span>{html.escape(date)}</span>' if date else ''}
      </div>

      <h1 dir="auto" class="text-2xl sm:text-3xl font-extrabold text-gray-900 dark:text-white leading-tight mb-2">
        {html.escape(title)}
      </h1>

      {f'<p dir="auto" class="text-sm sm:text-base text-gray-600 dark:text-zinc-400">{html.escape(subtitle)}</p>' if subtitle else ''}
    </header>

    {toc_html}

    <!-- بدنه پردازش‌شده مقاله -->
    <article id="article-content" class="article-prose text-gray-800 dark:text-zinc-200">
      {body_html}
    </article>

    <!-- پانویس مقاله -->
    <footer class="mt-14 pt-6 border-t border-gray-200 dark:border-zinc-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-gray-500 dark:text-zinc-400">
      <div>طراحی شده برای مطالعه بهینه متون تحلیلی و آموزشی</div>
      <button onclick="window.scrollTo({{top: 0, behavior: 'smooth'}})" class="hover:text-blue-600 transition flex items-center gap-1 font-medium">
        ↑ بازگشت به بالا
      </button>
    </footer>

  </main>

  <!-- اسکریپت‌های تعاملی خوانش -->
  <script>
    const FONT_MIN = 0.8, FONT_MAX = 1.3, FONT_STEP = 0.08, FONT_DEFAULT = 1; // FONT_DEFAULT = 1rem = 16px
    const LH_MIN = 1.6, LH_MAX = 2.6, LH_STEP = 0.12, LH_DEFAULT = 2.18;
    const PREFS_KEY = 'articleReaderPrefs';

    function loadPrefs() {{
      try {{
        const raw = localStorage.getItem(PREFS_KEY);
        return raw ? JSON.parse(raw) : {{}};
      }} catch (e) {{
        return {{}};
      }}
    }}

    function savePrefs() {{
      try {{
        localStorage.setItem(PREFS_KEY, JSON.stringify(prefs));
      }} catch (e) {{
        /* localStorage در دسترس نیست (مثلاً حالت خصوصی مرورگر)؛ بی‌خیال ذخیره می‌شویم */
      }}
    }}

    const prefs = loadPrefs();
    let currentFontSizeRem = prefs.fontSize || FONT_DEFAULT;
    let currentLineHeight = prefs.lineHeight || LH_DEFAULT;
    document.documentElement.style.setProperty('--article-font-size', `${{currentFontSizeRem}}rem`);
    document.documentElement.style.setProperty('--article-line-height', currentLineHeight);

    function changeFontSize(direction) {{
      currentFontSizeRem = Math.min(Math.max(currentFontSizeRem + (direction * FONT_STEP), FONT_MIN), FONT_MAX);
      document.documentElement.style.setProperty('--article-font-size', `${{currentFontSizeRem}}rem`);
      prefs.fontSize = currentFontSizeRem;
      savePrefs();
    }}

    function resetFontSize() {{
      currentFontSizeRem = FONT_DEFAULT;
      document.documentElement.style.setProperty('--article-font-size', `${{FONT_DEFAULT}}rem`);
      prefs.fontSize = currentFontSizeRem;
      savePrefs();
    }}

    function changeLineHeight(direction) {{
      currentLineHeight = Math.min(Math.max(currentLineHeight + (direction * LH_STEP), LH_MIN), LH_MAX);
      document.documentElement.style.setProperty('--article-line-height', currentLineHeight);
      prefs.lineHeight = currentLineHeight;
      savePrefs();
    }}

    function resetLineHeight() {{
      currentLineHeight = LH_DEFAULT;
      document.documentElement.style.setProperty('--article-line-height', LH_DEFAULT);
      prefs.lineHeight = currentLineHeight;
      savePrefs();
    }}

    const THEME_BUTTON_CLASS = {{
      auto: 'px-2 py-1 rounded transition bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300 font-semibold shadow-xs',
      light: 'px-2 py-1 rounded transition bg-white text-gray-900 font-semibold shadow-xs',
      sepia: 'px-2 py-1 rounded transition bg-[#e8decc] text-[#433422] font-semibold shadow-xs',
      dark: 'px-2 py-1 rounded transition bg-zinc-700 text-white font-semibold shadow-xs',
    }};

    function applyEffectiveTheme(effectiveTheme) {{
      const body = document.body;
      body.classList.remove('theme-light', 'theme-sepia', 'theme-dark');
      body.classList.add(`theme-${{effectiveTheme}}`);
      document.documentElement.classList.toggle('dark', effectiveTheme === 'dark');
    }}

    function highlightThemeButton(selected) {{
      const buttons = {{
        auto: document.getElementById('btn-auto'),
        light: document.getElementById('btn-light'),
        sepia: document.getElementById('btn-sepia'),
        dark: document.getElementById('btn-dark'),
      }};
      Object.values(buttons).forEach(btn => {{
        if (btn) btn.className = 'px-2 py-1 rounded transition text-gray-600 dark:text-zinc-400';
      }});
      if (buttons[selected]) buttons[selected].className = THEME_BUTTON_CLASS[selected];
    }}

    function systemPrefersDark() {{
      return !!(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
    }}

    function setTheme(theme) {{
      prefs.theme = theme;
      savePrefs();
      highlightThemeButton(theme);
      applyEffectiveTheme(theme === 'auto' ? (systemPrefersDark() ? 'dark' : 'light') : theme);
    }}

    if (window.matchMedia) {{
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {{
        if (prefs.theme === 'auto') applyEffectiveTheme(e.matches ? 'dark' : 'light');
      }});
    }}

    setTheme(prefs.theme || 'auto');

    window.addEventListener('scroll', () => {{
      const winScroll = document.documentElement.scrollTop || document.body.scrollTop;
      const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const scrolled = height > 0 ? (winScroll / height) * 100 : 0;
      const bar = document.getElementById('progress-bar');
      if (bar) {{
        bar.style.width = scrolled + '%';
      }}
    }});
  </script>
</body>
</html>
"""
