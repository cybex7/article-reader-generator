"""CLI: convert a text file/URL into a reading-page HTML, or run the local web server."""

from __future__ import annotations

import argparse
import re
import sys
from http.server import HTTPServer
from pathlib import Path

from .markdown_parser import MarkdownArticleParser
from .parser import ArticleParser
from .server import ArticleReaderRequestHandler
from .template import ReaderHTMLTemplate
from .url_import import UrlFetchError, fetch_article

MARKDOWN_EXTENSIONS = {".md", ".markdown"}


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert text into a standard, ergonomic reading-page HTML")
    parser.add_argument("input", nargs="?", help="Path to the input text file (txt or md)")
    parser.add_argument("-o", "--output", help="Path to save the output HTML")
    parser.add_argument("-t", "--title", default="", help="Article title")
    parser.add_argument("-a", "--author", default="", help="Author name")
    parser.add_argument("-d", "--date", default="", help="Publish date")
    parser.add_argument("-u", "--url", help="Web page URL to fetch and auto-extract article text from (instead of an input file)")
    parser.add_argument(
        "-f", "--format",
        choices=["auto", "plain", "markdown"],
        default="auto",
        help="How to process the text: auto (default, based on file extension/URL), plain (simple notes), or markdown (full)",
    )
    parser.add_argument("--serve", action="store_true", help="Run the local web server to use the graphical interface")
    parser.add_argument("--port", type=int, default=8080, help="Local web server port (default: 8080)")
    return parser


def serve(port: int) -> None:
    httpd = HTTPServer(('', port), ArticleReaderRequestHandler)
    print("\n[+] Local server started successfully.")
    print("[+] Open your browser and go to the address below:")
    print(f"    http://localhost:{port}\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Server stopped.")


def format_read_time(minutes: int) -> str:
    unit = "minute" if minutes == 1 else "minutes"
    return f"{minutes} {unit}"


def slugify_filename(title: str) -> str:
    trimmed = (title or "article").strip()
    return re.sub(r"\s+", "_", trimmed) or "article"


def render_article(title: str, author: str, date: str, raw_text: str, format: str) -> tuple[str, int]:
    parser_cls = MarkdownArticleParser if format == "markdown" else ArticleParser
    article = parser_cls.parse(raw_text)
    full_html = ReaderHTMLTemplate.render(
        title=title,
        subtitle="",
        author=author,
        date=date,
        content_html=article.content_html,
        read_time=article.read_time,
        toc=article.toc,
        format=format,
    )
    return full_html, article.read_time


def convert_file(input_path: Path, output: str | None, title: str, author: str, date: str, format: str) -> tuple[Path, int]:
    raw_text = input_path.read_text(encoding="utf-8")
    resolved_title = title or input_path.stem.replace('_', ' ').replace('-', ' ')
    resolved_format = format if format != "auto" else (
        "markdown" if input_path.suffix.lower() in MARKDOWN_EXTENSIONS else "plain"
    )
    full_html, read_time = render_article(resolved_title, author, date, raw_text, resolved_format)

    output_path = Path(output) if output else input_path.with_suffix(".html")
    output_path.write_text(full_html, encoding="utf-8")
    return output_path, read_time


def convert_url(url: str, output: str | None, title: str, author: str, date: str, format: str) -> tuple[Path, int]:
    fetched = fetch_article(url)
    resolved_title = title or fetched.title or "بدون عنوان"
    resolved_author = author or fetched.author
    resolved_date = date or fetched.date
    # Content fetched from the web is always extracted as Markdown
    resolved_format = format if format != "auto" else "markdown"
    full_html, read_time = render_article(resolved_title, resolved_author, resolved_date, fetched.content, resolved_format)

    output_path = Path(output) if output else Path(f"{slugify_filename(resolved_title)}.html")
    output_path.write_text(full_html, encoding="utf-8")
    return output_path, read_time


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.serve:
        serve(args.port)
        return

    if args.input and args.url:
        print("Error: cannot specify both an input file and a web URL (--url) at the same time.")
        sys.exit(1)

    if args.url:
        try:
            output_path, read_time = convert_url(args.url, args.output, args.title, args.author, args.date, args.format)
        except UrlFetchError as e:
            print(f"Error: {e}")
            sys.exit(1)
        print(f"\n[✓] Page created successfully: {output_path}")
        print(f"[i] Estimated reading time: {format_read_time(read_time)}\n")
        return

    if not args.input:
        parser.print_help()
        print("\nQuick examples:")
        print("  article-reader input.txt -o output.html --title 'Sociology Basics'")
        print("  article-reader notes.md -o output.html")
        print("  article-reader --url https://example.com/some-article -o output.html")
        print("  article-reader --serve")
        return

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file '{args.input}' not found.")
        sys.exit(1)

    output_path, read_time = convert_file(input_path, args.output, args.title, args.author, args.date, args.format)

    print(f"\n[✓] Page created successfully: {output_path}")
    print(f"[i] Estimated reading time: {format_read_time(read_time)}\n")


if __name__ == "__main__":
    main()
