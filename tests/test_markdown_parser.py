from article_reader.markdown_parser import MarkdownArticleParser


def test_parses_heading_with_sequential_id():
    article = MarkdownArticleParser.parse("# سرتیتر یک\n\nمتن.")
    assert '<h1 dir="auto" id="heading-1">سرتیتر یک</h1>' in article.content_html


def test_toc_includes_nested_heading_levels():
    text = "# سرتیتر یک\n\nمتن اول\n\n## زیرعنوان\n\nمتن دوم"
    article = MarkdownArticleParser.parse(text)
    levels = [(entry.level, entry.anchor_id) for entry in article.toc]
    assert levels == [(1, "heading-1"), (2, "heading-2")]


def test_toc_has_single_entry_for_single_heading():
    # نمایش/عدم‌نمایش فهرست مطالب برای تک‌سرتیتر در لایه‌ی قالب (template.py) تصمیم‌گیری می‌شود، نه پارسر
    article = MarkdownArticleParser.parse("# تنها سرتیتر\n\nمتن.")
    assert len(article.toc) == 1
    assert article.toc[0].anchor_id == "heading-1"


def test_bold_italic_link_and_inline_code():
    html = MarkdownArticleParser.parse(
        "این **بولد** و *ایتالیک* و [لینک](https://example.com) و `کد`."
    ).content_html
    assert "<strong>بولد</strong>" in html
    assert "<em>ایتالیک</em>" in html
    assert '<a href="https://example.com">لینک</a>' in html
    assert "<code>کد</code>" in html


def test_blockquote_maps_to_card_box():
    html = MarkdownArticleParser.parse("> نقل قول مهم").content_html
    assert "card-box" in html
    assert "<blockquote>" not in html


def test_table_is_wrapped_for_horizontal_scroll():
    text = "| ستون ۱ | ستون ۲ |\n| --- | --- |\n| الف | ب |"
    html = MarkdownArticleParser.parse(text).content_html
    assert '<div class="overflow-x-auto' in html
    assert "<table" in html


def test_fenced_code_block():
    text = "```python\nx = 1\n```"
    html = MarkdownArticleParser.parse(text).content_html
    assert "<pre>" in html
    assert "x = 1" in html


def test_image_renders_as_img_tag():
    html = MarkdownArticleParser.parse("![توضیح](pic.png)").content_html
    assert '<img alt="توضیح" src="pic.png"' in html


def test_nested_list_with_two_space_indent():
    text = "- آیتم یک\n  - زیرآیتم\n- آیتم دو"
    html = MarkdownArticleParser.parse(text).content_html
    assert '<li dir="auto">آیتم یک<ul>' in html or '<li dir="auto">آیتم یک\n<ul>' in html


def test_raw_html_in_source_passes_through():
    html = MarkdownArticleParser.parse("<script>alert(1)</script>").content_html
    assert "<script>alert(1)</script>" in html


def test_english_paragraph_gets_dir_auto_for_bidi_detection():
    html = MarkdownArticleParser.parse("This is an English paragraph.").content_html
    assert '<p dir="auto">This is an English paragraph.</p>' in html


def test_table_cells_get_dir_auto():
    text = "| a | b |\n| --- | --- |\n| 1 | 2 |"
    html = MarkdownArticleParser.parse(text).content_html
    assert 'dir="auto"' in html
    assert '<th dir="auto">' in html or '<td dir="auto">' in html
