"""دریافت یک صفحه‌ی وب و استخراج متن خالص مقاله از آن (بدون منو، تبلیغ، سایدبار و...)."""

from __future__ import annotations

from dataclasses import dataclass

import trafilatura


class UrlFetchError(Exception):
    """صفحه قابل دریافت یا متن اصلی آن قابل استخراج نبود."""


@dataclass
class FetchedArticle:
    title: str
    author: str
    date: str
    content: str


def fetch_article(url: str) -> FetchedArticle:
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        raise UrlFetchError(f"امکان دریافت صفحه از آدرس داده‌شده وجود نداشت: {url}")

    content = trafilatura.extract(
        downloaded,
        output_format="markdown",
        include_links=True,
        include_images=True,
        include_tables=True,
        include_formatting=True,
    )
    if not content:
        raise UrlFetchError("متن اصلی مقاله از این صفحه قابل استخراج نبود.")

    metadata = trafilatura.extract_metadata(downloaded)

    return FetchedArticle(
        title=(metadata.title if metadata and metadata.title else ""),
        author=(metadata.author if metadata and metadata.author else ""),
        date=(metadata.date if metadata and metadata.date else ""),
        content=content,
    )
