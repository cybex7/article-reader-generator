"""Article Reader Generator — مبدل متن به صفحه مطالعه HTML استاندارد."""

from .parser import ArticleParser, ParsedArticle, TocEntry
from .template import ReaderHTMLTemplate

__all__ = [
    "ArticleParser",
    "ParsedArticle",
    "TocEntry",
    "ReaderHTMLTemplate",
]

__version__ = "1.0.0"
