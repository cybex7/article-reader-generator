/**
 * Cloudflare Worker: یک آدرس وب می‌گیرد، صفحه را دریافت می‌کند، متن اصلی مقاله
 * (بدون منو/تبلیغ/سایدبار) را با الگوریتم Readability موزیلا استخراج می‌کند و
 * به‌صورت Markdown برمی‌گرداند — دقیقاً هم‌شکل خروجی endpoint پایتونی /fetch-url.
 *
 * چون این Worker سمت سرور/edge اجرا می‌شود، محدودیت CORS مرورگر برای *دریافت*
 * صفحه‌ی هدف وجود ندارد؛ پاسخ خودِ Worker هم با هدر CORS باز برگردانده می‌شود تا
 * از هر صفحه‌ی استاتیک (GitHub Pages، Cloudflare Pages و ...) قابل فراخوانی باشد.
 */

import { parseHTML, DOMParser, HTMLElement } from 'linkedom';
import { Readability } from '@mozilla/readability';

// turndown در همان لحظه import شدن وجود window.DOMParser را بررسی می‌کند (نه هنگام اجرا)
// پس این Globalها باید قبل از import ماژول turndown ست شده باشند - به همین دلیل
// turndown را با import پویا (بعد از ست‌کردن Globalها) بارگذاری می‌کنیم، نه import ثابت.
if (typeof globalThis.window === 'undefined') {
  globalThis.window = globalThis;
}
if (typeof globalThis.DOMParser === 'undefined') {
  globalThis.DOMParser = DOMParser;
}

// حالت سبک linkedom همه‌ی تگ‌ها را با یک کلاس عمومی HTMLElement می‌سازد (نه
// HTMLTableElement اختصاصی)، پس مجموعه‌ی زنده‌ی .rows اصلاً وجود ندارد؛ در حالی که
// پلاگین جدول turndown-plugin-gfm فقط وقتی به .rows دسترسی پیدا می‌کند که
// nodeName از قبل 'TABLE' باشد، پس افزودن این getter به کلاس عمومی بی‌خطر است.
if (!('rows' in HTMLElement.prototype)) {
  Object.defineProperty(HTMLElement.prototype, 'rows', {
    get() {
      return Array.from(this.querySelectorAll(':scope > tr, :scope > thead > tr, :scope > tbody > tr, :scope > tfoot > tr'));
    },
  });
}

const { default: TurndownService } = await import('turndown');
const { gfm } = await import('turndown-plugin-gfm');

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      ...CORS_HEADERS,
    },
  });
}

function htmlToMarkdown(html) {
  const turndownService = new TurndownService({
    headingStyle: 'atx',
    codeBlockStyle: 'fenced',
    bulletListMarker: '-',
  });
  turndownService.use(gfm);
  return turndownService.turndown(html);
}

export default {
  async fetch(request) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS_HEADERS });
    }

    if (request.method !== 'GET') {
      return jsonResponse({ error: 'فقط متد GET پشتیبانی می‌شود.' }, 405);
    }

    const requestUrl = new URL(request.url);
    const targetUrl = requestUrl.searchParams.get('url');

    if (!targetUrl) {
      return jsonResponse({ error: 'پارامتر url ارسال نشده است.' }, 400);
    }

    let parsedTargetUrl;
    try {
      parsedTargetUrl = new URL(targetUrl);
      if (!['http:', 'https:'].includes(parsedTargetUrl.protocol)) {
        throw new Error('invalid protocol');
      }
    } catch (e) {
      return jsonResponse({ error: 'آدرس وارد شده معتبر نیست.' }, 400);
    }

    let pageResponse;
    try {
      pageResponse = await fetch(parsedTargetUrl.toString(), {
        headers: {
          'User-Agent': 'Mozilla/5.0 (compatible; ArticleReaderBot/1.0; +https://github.com/)',
        },
        redirect: 'follow',
      });
    } catch (e) {
      return jsonResponse({ error: 'امکان دریافت این صفحه وجود نداشت.' }, 400);
    }

    if (!pageResponse.ok) {
      return jsonResponse({ error: `صفحه با کد وضعیت ${pageResponse.status} پاسخ داد.` }, 400);
    }

    const html = await pageResponse.text();

    let article;
    try {
      const { document } = parseHTML(html);

      // Readability برای حل لینک‌ها/تصاویر نسبی به baseURI نیاز دارد
      const base = document.createElement('base');
      base.setAttribute('href', parsedTargetUrl.toString());
      (document.head || document.documentElement).appendChild(base);

      article = new Readability(document).parse();
    } catch (e) {
      return jsonResponse({ error: 'پردازش HTML این صفحه با خطا مواجه شد: ' + e.message }, 400);
    }

    if (!article || !article.content) {
      return jsonResponse({ error: 'متن اصلی مقاله از این صفحه قابل استخراج نبود.' }, 400);
    }

    let markdown;
    try {
      markdown = htmlToMarkdown(article.content);
    } catch (e) {
      console.error('turndown failed:', e.stack || e.message);
      // اگر تبدیل به Markdown با خطا مواجه شد، حداقل متن خام مقاله را برمی‌گردانیم
      markdown = article.textContent || '';
    }

    return jsonResponse({
      title: article.title || '',
      author: article.byline || '',
      date: article.publishedTime || '',
      content: markdown,
    });
  },
};
