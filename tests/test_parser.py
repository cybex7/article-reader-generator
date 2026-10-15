from article_reader.parser import ArticleParser


def test_calculate_read_time_rounds_up_to_at_least_one_minute():
    assert ArticleParser.calculate_read_time("چند کلمه کوتاه") == 1


def test_calculate_read_time_scales_with_word_count():
    text = " ".join(["کلمه"] * 400)
    assert ArticleParser.calculate_read_time(text) == 2


def test_parse_inline_bold_and_italic():
    html_out = ArticleParser.parse_inline("این **مهم** و این *تاکید* است")
    assert "<strong" in html_out
    assert "مهم</strong>" in html_out
    assert "<em>تاکید</em>" in html_out


def test_parse_inline_escapes_html_to_prevent_injection():
    html_out = ArticleParser.parse_inline("<script>alert(1)</script>")
    assert "<script>" not in html_out
    assert "&lt;script&gt;" in html_out


def test_parse_produces_paragraph():
    article = ArticleParser.parse("این یک بند ساده است.")
    assert '<p dir="auto">این یک بند ساده است.</p>' in article.content_html


def test_parse_builds_unordered_list():
    article = ArticleParser.parse("- مورد اول\n- مورد دوم")
    assert "<ul" in article.content_html
    assert '<li dir="auto">مورد اول</li>' in article.content_html
    assert '<li dir="auto">مورد دوم</li>' in article.content_html


def test_parse_builds_ordered_list():
    article = ArticleParser.parse("1- مورد اول\n2- مورد دوم")
    assert "<ol" in article.content_html


def test_parse_detects_quote_box():
    article = ArticleParser.parse("> این یک نکته کلیدی است")
    assert 'card-box' in article.content_html


def test_parse_generates_toc_entries_for_numbered_sections():
    text = "1. مقدمه\nمتن اول\n\n2. نتیجه‌گیری\nمتن دوم"
    article = ArticleParser.parse(text)
    assert [entry.anchor_id for entry in article.toc] == ["section-1", "section-2"]
    assert article.toc[0].title == "مقدمه"
    assert 'id="section-1"' in article.content_html


def test_parse_toc_is_empty_with_no_headings():
    article = ArticleParser.parse("فقط یک بند بدون سرتیتر.")
    assert article.toc == []


def test_parse_to_html_backward_compatible_helper():
    assert ArticleParser.parse_to_html("متن ساده") == ArticleParser.parse("متن ساده").content_html


def test_english_paragraph_gets_dir_auto_for_bidi_detection():
    # هر بند باید جهت خودش رو بر اساس محتوای خودش تشخیص بده (مثل تلگرام)،
    # نه اینکه از جهت raw ثابت کل صفحه (rtl) ارث ببره.
    article = ArticleParser.parse("This is an English paragraph.")
    assert '<p dir="auto">This is an English paragraph.</p>' in article.content_html
