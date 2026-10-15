# Article Reader Generator 📖✨

*[نسخه فارسی](README.md)*

Turns plain text or lightweight-markdown notes into a single, self-contained HTML reading page — optimized for Persian (RTL) typography and reading ergonomics, but usable for any text.

## 🧭 Which version should I use?

This repo ships **two independent, fully usable versions** that produce the same look and reading experience — they just run in different places:

| | 🐍 Python version (`src/`) | 🌐 Static web version (`web/`) |
| :--- | :--- | :--- |
| **Runs where** | On your own machine (CLI or local server) | In the browser — deployable to GitHub Pages / Cloudflare Pages |
| **Install needed** | Python 3.10+ (`pip install -e .`) | None — just open an HTML page |
| **Best for** | Personal day-to-day use, batch-converting files from the CLI, scripting/automation | Shipping this as a web tool anyone (even without Python) can use from any browser |
| **Fetch from a URL** | ✅ Built in and ready (`--url`, via `trafilatura`) | Needs a separate Worker (CORS) — ready in [`cloudflare-worker/`](cloudflare-worker/) |
| **Full guide** | The "💻 Usage" section below | [web/README.md](web/README.md) |

Not sure which to pick: for personal use on your own machine, the Python version is simpler; if you want to hand this to others (or use it yourself from any device) as a web page, go with `web/`.

## 🌟 Key Features

- **Optimal line length:** a 740px-wide reading column (roughly 60–75 characters per line) to reduce eye strain.
- **Persian-first typography:** the **Vazirmatn** font with a generous `line-height: 2.18`.
- **Full Markdown support:** `.md`/`.markdown` files (or content fetched from the web) get full standard Markdown handling — headings, bold/italic, nested lists, blockquotes, links, images, tables, and code blocks. Plain notes still use the lightweight heuristic parser (numbered headings, `a)`, `💡`); the mode is auto-detected from the file extension or can be set manually.
- **Automatic table of contents:** a collapsible TOC generated from numbered section headings (plain mode) or from all heading levels with indentation (Markdown mode).
- **Three reading themes:** Light, Sepia (paper-like), and Dark.
- **Font-size control:** one-click zoom in/out without breaking the layout.
- **Live reading-progress bar** at the top of the page.
- **Estimated reading time**, based on ~200 words per minute.
- **Drag-and-drop upload:** in the web UI, drop a `.txt`/`.md` file onto the form (or click to pick one) instead of pasting text.
- **Fetch directly from a URL:** paste an article link and its main text (stripped of nav/ads/sidebars) is extracted automatically (via `trafilatura`).
- **Standalone output:** the generated page is a single HTML file (styling via CDN) that needs no runtime or framework to *view* — though the generator itself has a Python dependency.
- **Two ways to use it:** a CLI, and a local web UI.

---

## 🚀 Install

Requires **Python 3.10+**.

```bash
pip install -e .
```

This installs the `article-reader` command.

---

## 💻 Usage

### 1. Local web UI (easiest)

```bash
article-reader --serve
```

Open `http://localhost:8080`, paste your text (or drag & drop a file), and click the button to download the generated HTML page.

### 2. Command line

```bash
article-reader examples/sample_article.txt \
  --title "Sociology Basics" \
  --author "Jane Doe" \
  --date "Session 1" \
  -o sociology_lesson1.html
```

Or straight from a URL:

```bash
article-reader --url "https://example.com/some-article" -o article.html
```

| Argument | Description |
| :--- | :--- |
| `input` | Path to the input text/markdown file |
| `-u`, `--url` | Web page URL to fetch and auto-extract article text from (instead of a file) |
| `-o`, `--output` | Output HTML path (default: same name as input, or derived from the title in `--url` mode) |
| `-t`, `--title` | Article title (auto-extracted in `--url` mode if left blank) |
| `-a`, `--author` | Author name |
| `-d`, `--date` | Date or session label |
| `-f`, `--format` | Content mode: `auto` (default, from file extension/URL), `plain`, or `markdown` |
| `--serve` | Run the local web server with the UI |
| `--port` | Server port (default: 8080) |

---

## 🌐 Web version (browser-only, GitHub Pages ready)

The [`web/`](web/) folder is a fully static, dependency-free-at-runtime version that runs entirely in the browser (no server) — including full Markdown support via `markdown-it`. See [web/README.md](web/README.md) for local testing instructions.

For URL-fetch support on that static site, [`cloudflare-worker/`](cloudflare-worker/) is a standalone JS Worker (using Mozilla's Readability) that solves the CORS problem a static site can't — see [cloudflare-worker/README.md](cloudflare-worker/README.md).

---

## 🧪 Running tests

```bash
pip install -e ".[dev]"
pytest
```

---

## 📁 Repository layout

```text
├── src/article_reader/     # parser, HTML template, web server, CLI (Python)
│   ├── parser.py
│   ├── template.py
│   ├── server.py
│   ├── url_import.py
│   ├── markdown_parser.py
│   └── cli.py
├── web/                     # static browser-only version (JavaScript, GitHub Pages ready)
│   ├── index.html
│   ├── js/
│   └── README.md
├── tests/                  # pytest test suite
├── examples/
│   └── sample_article.txt  # sample input for a quick try
├── pyproject.toml
└── README.md
```

---

## 📄 License

[MIT](LICENSE) — free for personal and commercial use.
