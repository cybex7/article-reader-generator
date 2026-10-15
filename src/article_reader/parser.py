"""تجزیه‌کننده متن ساده/مارک‌داون به بلوک‌های معنایی HTML."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field


@dataclass
class TocEntry:
    """یک ردیف از فهرست مطالب."""

    anchor_id: str
    title: str
    level: int = 1


@dataclass
class ParsedArticle:
    """خروجی کامل تجزیه: بدنه HTML، فهرست مطالب و زمان مطالعه."""

    content_html: str
    toc: list[TocEntry] = field(default_factory=list)
    read_time: int = 1


class ArticleParser:
    """تجزیه‌کننده ساختار متن و نشانه‌گذاری‌ها به بلوک‌های معنایی HTML"""

    @staticmethod
    def calculate_read_time(text: str) -> int:
        """محاسبه تقریبی زمان مطالعه بر مبنای ۲۰۰ کلمه در دقیقه"""
        words = len(re.findall(r'\S+', text))
        minutes = max(1, round(words / 200))
        return minutes

    @staticmethod
    def parse_inline(text: str) -> str:
        """تبدیل نشانه‌گذاری‌های درون‌متنی نظیر ضخیم و ایتالیک"""
        # جلوگیری از تزریق HTML/اسکریپت از سمت کاربر
        text = html.escape(text)
        # تبدیل خط تیره بلند
        text = text.replace('--', '—')
        # بولد با ** یا __
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong class="text-gray-900 dark:text-white">\1</strong>', text)
        text = re.sub(r'__(.+?)__', r'<strong class="text-gray-900 dark:text-white">\1</strong>', text)
        # ایتالیک با * یا _
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
        return text

    @classmethod
    def parse(cls, raw_text: str) -> ParsedArticle:
        """تجزیه کامل متن: بدنه HTML + فهرست مطالب + زمان مطالعه"""
        lines = raw_text.strip().splitlines()
        html_blocks: list[str] = []
        toc: list[TocEntry] = []
        in_list = False
        list_type = "ul"
        section_number = 1

        for line in lines:
            line_str = line.strip()

            if not line_str:
                if in_list:
                    html_blocks.append(f"</{list_type}>")
                    in_list = False
                continue

            # تشخیص بخش‌های اصلی با شماره‌گذاری (مانند: ۱. یا #)
            heading1_match = re.match(r'^(?:#\s*|[۰-۹0-9]+\.\s*)(.+)$', line_str)
            heading2_match = re.match(r'^(?:##\s*|[الف-ی]\)\s*)(.+)$', line_str)
            heading3_match = re.match(r'^(?:###\s*)(.+)$', line_str)

            if heading1_match and not line_str.startswith('---'):
                if in_list:
                    html_blocks.append(f"</{list_type}>")
                    in_list = False
                title_text = heading1_match.group(1).strip()
                anchor_id = f"section-{section_number}"
                toc.append(TocEntry(anchor_id=anchor_id, title=cls.parse_inline(title_text)))
                html_blocks.append(f"""
                <div id="{anchor_id}" class="flex items-center gap-3 mt-10 mb-4 scroll-mt-20">
                  <span class="w-8 h-8 rounded-lg bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-200 font-bold flex items-center justify-center text-sm">{section_number}</span>
                  <h2 dir="auto" class="text-lg sm:text-xl font-bold text-gray-900 dark:text-white">{cls.parse_inline(title_text)}</h2>
                </div>
                """)
                section_number += 1
                continue

            if heading2_match:
                if in_list:
                    html_blocks.append(f"</{list_type}>")
                    in_list = False
                subtitle_text = heading2_match.group(1).strip()
                html_blocks.append(f"""
                <h3 dir="auto" class="text-base sm:text-lg font-bold text-gray-900 dark:text-zinc-100 mt-6 mb-3 flex items-center gap-2">
                  <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                  {cls.parse_inline(subtitle_text)}
                </h3>
                """)
                continue

            if heading3_match:
                if in_list:
                    html_blocks.append(f"</{list_type}>")
                    in_list = False
                sub_text = heading3_match.group(1).strip()
                html_blocks.append(f'<h4 dir="auto" class="font-bold text-sm text-gray-900 dark:text-white mt-4 mb-2">{cls.parse_inline(sub_text)}</h4>')
                continue

            # تشخیص نقل‌قول‌ها یا جعبه‌های نکته کلیدی (مانند > یا 💡 یا نتیجه:)
            if line_str.startswith('>') or line_str.startswith('💡') or line_str.startswith('نتیجه:'):
                if in_list:
                    html_blocks.append(f"</{list_type}>")
                    in_list = False
                clean_quote = re.sub(r'^[>💡\s]+', '', line_str)
                html_blocks.append(f"""
                <div class="card-box p-4 sm:p-5 my-5 rounded-2xl border transition-all">
                  <p dir="auto" class="!mb-0 text-sm sm:text-base leading-relaxed">
                    {cls.parse_inline(clean_quote)}
                  </p>
                </div>
                """)
                continue

            # تشخیص آیتم‌های لیست (-, *, یا ارقام)
            list_item_match = re.match(r'^[-*•]\s+(.+)$', line_str)
            ordered_item_match = re.match(r'^[۰-۹0-9]+[-)]\s+(.+)$', line_str)

            if list_item_match:
                if not in_list or list_type != "ul":
                    if in_list:
                        html_blocks.append(f"</{list_type}>")
                    html_blocks.append('<ul class="space-y-2.5 pr-5 list-disc text-gray-700 dark:text-zinc-300 mb-5">')
                    in_list = True
                    list_type = "ul"
                html_blocks.append(f'<li dir="auto">{cls.parse_inline(list_item_match.group(1))}</li>')
                continue

            if ordered_item_match:
                if not in_list or list_type != "ol":
                    if in_list:
                        html_blocks.append(f"</{list_type}>")
                    html_blocks.append('<ol class="space-y-2 pr-5 list-decimal text-gray-700 dark:text-zinc-300 mb-5">')
                    in_list = True
                    list_type = "ol"
                html_blocks.append(f'<li dir="auto">{cls.parse_inline(ordered_item_match.group(1))}</li>')
                continue

            # بند معمولی متن (Paragraph)
            if in_list:
                html_blocks.append(f"</{list_type}>")
                in_list = False

            html_blocks.append(f'<p dir="auto">{cls.parse_inline(line_str)}</p>')

        if in_list:
            html_blocks.append(f"</{list_type}>")

        return ParsedArticle(
            content_html="\n".join(html_blocks),
            toc=toc,
            read_time=cls.calculate_read_time(raw_text),
        )

    @classmethod
    def parse_to_html(cls, raw_text: str) -> str:
        """سازگاری با نسخه‌های قبلی: فقط بدنه HTML را برمی‌گرداند"""
        return cls.parse(raw_text).content_html
