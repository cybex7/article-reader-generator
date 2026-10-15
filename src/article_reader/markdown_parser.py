"""پارس کامل Markdown با python-markdown، برای فایل‌های .md یا متن دریافت‌شده از وب.

برخلاف ArticleParser (هیوریستیک متن ساده/یادداشت)، اینجا از قوانین استاندارد
Markdown/GFM پیروی می‌شود: سرتیتر با #، بولد/ایتالیک، لیست‌های تودرتو، نقل‌قول،
بلاک/کد درون‌خطی، لینک، تصویر، جدول، خط افقی.
"""

from __future__ import annotations

import itertools
import re

import markdown as md_lib
from markdown.extensions.toc import TocExtension

from .parser import ArticleParser, ParsedArticle, TocEntry

# سرتیتر، پاراگراف، آیتم لیست و سلول جدول هرکدام باید جهت خودشون رو بر اساس
# محتوای خودشون تشخیص بدن (مثل تلگرام) نه ارثی از جهت کل صفحه بگیرن.
_DIR_AUTO_TAGS = re.compile(r'<(h[1-6]|p|li|td|th)((?:\s[^>]*)?)>')


def _add_dir_auto(html: str) -> str:
    return _DIR_AUTO_TAGS.sub(r'<\1 dir="auto"\2>', html)


def _sequential_slugify(_counter):
    def _slugify(_value: str, _separator: str) -> str:
        return f"heading-{next(_counter)}"

    return _slugify


def _wrap_tables(html: str) -> str:
    html = html.replace(
        "<table>",
        '<div class="overflow-x-auto my-6"><table class="w-full text-sm border-collapse">',
    )
    return html.replace("</table>", "</table></div>")


def _blockquotes_to_card_boxes(html: str) -> str:
    html = html.replace(
        "<blockquote>",
        '<div class="card-box p-4 sm:p-5 my-5 rounded-2xl border transition-all">',
    )
    return html.replace("</blockquote>", "</div>")


def _flatten_toc(tokens: list[dict]) -> list[TocEntry]:
    flat: list[TocEntry] = []
    for token in tokens:
        flat.append(TocEntry(anchor_id=token["id"], title=token["name"], level=token["level"]))
        flat.extend(_flatten_toc(token.get("children", [])))
    return flat


class MarkdownArticleParser:
    """پارس کامل Markdown با استفاده از کتابخانه python-markdown."""

    @classmethod
    def parse(cls, raw_text: str) -> ParsedArticle:
        slugify = _sequential_slugify(itertools.count(1))
        instance = md_lib.Markdown(
            extensions=[
                "extra",
                "mdx_truly_sane_lists",
                TocExtension(slugify=slugify, anchorlink=False),
            ]
        )

        content_html = instance.convert(raw_text)
        content_html = _wrap_tables(content_html)
        content_html = _blockquotes_to_card_boxes(content_html)
        content_html = _add_dir_auto(content_html)

        toc = _flatten_toc(instance.toc_tokens or [])

        return ParsedArticle(
            content_html=content_html,
            toc=toc,
            read_time=ArticleParser.calculate_read_time(raw_text),
        )
