# Article Reader — Fetch Worker

یک Cloudflare Worker مستقل که یک آدرس وب می‌گیرد، صفحه را دریافت می‌کند، متن اصلی مقاله (بدون منو/تبلیغ/سایدبار) را با الگوریتم **Readability** موزیلا استخراج می‌کند و به‌صورت **Markdown** برمی‌گرداند.

این Worker دقیقاً همون قابلیتیه که نسخه‌ی پایتونی (`--url` در CLI، یا فیلد آدرس در `--serve`) با `trafilatura` انجام می‌ده، ولی چون Workers محیط اجرای پایتون رسمی و پایداری برای این حجم از وابستگی‌ها نداره، اینجا با کتابخانه‌های جاوااسکریپت پیاده‌سازی شده:

- **[linkedom](https://github.com/WebReflection/linkedom)** — یک پیاده‌سازی سبک DOM در JS خالص (چون Workers مثل مرورگر `document` واقعی نداره)
- **[@mozilla/readability](https://github.com/mozilla/readability)** — همون الگوریتمی که Reader Mode فایرفاکس رو می‌سازه
- **[turndown](https://github.com/mixmark-io/turndown)** + **[turndown-plugin-gfm](https://github.com/mixmark-io/turndown-plugin-gfm)** — تبدیل HTML تمیزشده به Markdown (با پشتیبانی جدول)

## چرا این Worker لازم بود؟ (نه فقط یک فایل استاتیک)

یک سایت کاملاً استاتیک (مثل `web/` همین ریپو، روی GitHub Pages یا Cloudflare Pages) به‌خاطر محدودیت **CORS** نمی‌تونه مستقیم از مرورگر کاربر، HTML یک دامنه‌ی دیگه رو fetch کنه. این Worker چون سمت سرور/edge اجرا می‌شه این محدودیت رو نداره، و پاسخش هم با هدر CORS باز (`Access-Control-Allow-Origin: *`) برمی‌گرده تا از هر صفحه‌ی استاتیکی قابل فراخوانی باشه.

## تست محلی (قبل از دیپلوی)

```bash
npm install
npm run dev
```

این با `wrangler dev` یک نسخه‌ی واقعی از محیط اجرای Workers (نه شبیه‌سازی) رو روی `http://localhost:8787` بالا میاره. تست کن:

```bash
curl "http://localhost:8787/?url=https://example.com"
```

خروجی: `{"title": "...", "author": "...", "date": "...", "content": "... به‌صورت Markdown ..."}`

## دیپلوی روی Cloudflare

```bash
npx wrangler login   # یک‌بار، برای وصل‌شدن به اکانت کلادفلر
npm run deploy
```

بعد از دیپلوی، آدرسی شبیه `https://article-reader-fetch.<your-subdomain>.workers.dev` بهت داده می‌شه. (پلن رایگان کلادفلر Workers فعلاً ۱۰۰ هزار درخواست در روز رایگانه.)

## نحوه‌ی API

```
GET /?url=<آدرس صفحه‌ی هدف>
```

پاسخ موفق (200):
```json
{ "title": "...", "author": "...", "date": "...", "content": "... Markdown ..." }
```

پاسخ خطا (400 یا 405):
```json
{ "error": "توضیح خطا به فارسی" }
```

## قدم بعدی: وصل‌کردن به نسخه‌ی وب

بعد از این‌که این Worker رو دیپلوی کردی و آدرسش رو داشتی، می‌تونیم یه فیلد «دریافت از آدرس وب» به `web/index.html` اضافه کنیم (دقیقاً مثل همونی که در رابط وب محلی پایتون هست) که همین Worker رو صدا بزنه و نتیجه رو مستقیم توی فرم پر کنه — تا نسخه‌ی وب/GitHub Pages هم این قابلیت رو داشته باشه. کافیه بگی آماده‌ای و آدرس Worker رو بدی.
