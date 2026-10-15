/**
 * پارس کامل Markdown با markdown-it (+ پلاگین جدول)، بارگذاری‌شده از CDN در index.html.
 * برخلاف parser-plain.js، اینجا از قوانین استاندارد CommonMark/GFM پیروی می‌کنیم:
 * سرتیتر با #، بولد/ایتالیک، لیست‌های تودرتو، نقل‌قول، بلاک/کد درون‌خطی، لینک، تصویر، جدول، خط افقی.
 */

let mdInstance = null;

function getMarkdownIt() {
  if (mdInstance) return mdInstance;

  const md = window.markdownit({ html: true, linkify: true, breaks: false });
  if (window.markdownitMultimdTable) {
    md.use(window.markdownitMultimdTable, { multiline: true, rowspan: true, headerless: false });
  }

  // نقل‌قول‌ها را به همان جعبه‌ی نکته‌ی بصری (card-box) مپ می‌کنیم
  md.renderer.rules.blockquote_open = () =>
    '<div class="card-box p-4 sm:p-5 my-5 rounded-2xl border transition-all">';
  md.renderer.rules.blockquote_close = () => '</div>';

  // جدول‌ها داخل یک کانتینر قابل اسکرول افقی قرار می‌گیرند تا در موبایل صفحه را بهم نریزند
  md.renderer.rules.table_open = () =>
    '<div class="overflow-x-auto my-6"><table class="w-full text-sm border-collapse">';
  md.renderer.rules.table_close = () => '</table></div>';

  mdInstance = md;
  return md;
}

function calculateReadTimeMarkdown(text) {
  const words = (text.match(/\S+/g) || []).length;
  return Math.max(1, Math.round(words / 200));
}

// این تگ‌ها باید جهت خودشون رو بر اساس محتوای خودشون تشخیص بدن (مثل تلگرام)
// نه ارثی از جهت کل صفحه بگیرن.
const DIR_AUTO_TOKEN_TYPES = new Set([
  'heading_open',
  'paragraph_open',
  'list_item_open',
  'th_open',
  'td_open',
]);

function parseMarkdownArticle(rawText) {
  const md = getMarkdownIt();
  const env = {};
  const tokens = md.parse(rawText, env);

  const toc = [];
  let headingCounter = 0;

  for (let i = 0; i < tokens.length; i += 1) {
    const token = tokens[i];

    if (DIR_AUTO_TOKEN_TYPES.has(token.type)) {
      token.attrSet('dir', 'auto');
    }

    if (token.type !== 'heading_open') continue;

    headingCounter += 1;
    const anchorId = `heading-${headingCounter}`;
    token.attrSet('id', anchorId);

    const level = parseInt(token.tag.slice(1), 10);
    const inlineToken = tokens[i + 1];
    const titleHtml = inlineToken && inlineToken.type === 'inline'
      ? md.renderer.renderInline(inlineToken.children, md.options, env)
      : '';

    toc.push({ anchorId, title: titleHtml, level });
  }

  const contentHtml = md.renderer.render(tokens, md.options, env);

  return {
    contentHtml,
    toc,
    readTime: calculateReadTimeMarkdown(rawText),
  };
}
