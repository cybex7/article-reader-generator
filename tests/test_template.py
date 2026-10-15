from article_reader.parser import TocEntry
from article_reader.template import ReaderHTMLTemplate


def _render(**overrides):
    defaults = dict(
        title="عنوان آزمایشی",
        subtitle="",
        author="",
        date="",
        content_html="<p>متن</p>",
        read_time=3,
        toc=None,
    )
    defaults.update(overrides)
    return ReaderHTMLTemplate.render(**defaults)


def test_render_includes_title_and_read_time():
    page = _render(title="مقاله من", read_time=5)
    assert "مقاله من" in page
    assert "5 دقیقه مطالعه" in page


def test_render_escapes_title_to_prevent_injection():
    page = _render(title="<script>alert(1)</script>")
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page


def test_render_without_toc_when_none_or_single_entry():
    page_none = _render(toc=None)
    page_single = _render(toc=[TocEntry(anchor_id="section-1", title="مقدمه")])
    assert "فهرست مطالب" not in page_none
    assert "فهرست مطالب" not in page_single


def test_render_includes_toc_when_multiple_entries():
    toc = [
        TocEntry(anchor_id="section-1", title="مقدمه"),
        TocEntry(anchor_id="section-2", title="نتیجه‌گیری"),
    ]
    page = _render(toc=toc)
    assert "فهرست مطالب" in page
    assert 'href="#section-1"' in page
    assert 'href="#section-2"' in page
