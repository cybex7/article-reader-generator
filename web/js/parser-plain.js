/**
 * پورت جاوااسکریپتی پارسر هیوریستیک متن ساده/یادداشت (معادل src/article_reader/parser.py)
 */

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function calculateReadTime(text) {
  const words = (text.match(/\S+/g) || []).length;
  return Math.max(1, Math.round(words / 200));
}

function parseInline(text) {
  let out = escapeHtml(text);
  out = out.replace(/--/g, '—');
  out = out.replace(/\*\*(.+?)\*\*/g, '<strong class="text-gray-900 dark:text-white">$1</strong>');
  out = out.replace(/__(.+?)__/g, '<strong class="text-gray-900 dark:text-white">$1</strong>');
  out = out.replace(/\*(.+?)\*/g, '<em>$1</em>');
  out = out.replace(/_(.+?)_/g, '<em>$1</em>');
  return out;
}

function parsePlainArticle(rawText) {
  const lines = rawText.trim().split(/\r?\n/);
  const htmlBlocks = [];
  const toc = [];
  let inList = false;
  let listType = 'ul';
  let sectionNumber = 1;

  const closeList = () => {
    if (inList) {
      htmlBlocks.push(`</${listType}>`);
      inList = false;
    }
  };

  for (const rawLine of lines) {
    const line = rawLine.trim();

    if (!line) {
      closeList();
      continue;
    }

    const heading1Match = line.match(/^(?:#\s*|[۰-۹0-9]+\.\s*)(.+)$/);
    const heading2Match = line.match(/^(?:##\s*|[الف-ی]\)\s*)(.+)$/);
    const heading3Match = line.match(/^(?:###\s*)(.+)$/);

    if (heading1Match && !line.startsWith('---')) {
      closeList();
      const titleText = heading1Match[1].trim();
      const anchorId = `section-${sectionNumber}`;
      const titleHtml = parseInline(titleText);
      toc.push({ anchorId, title: titleHtml, level: 1 });
      htmlBlocks.push(`
        <div id="${anchorId}" class="flex items-center gap-3 mt-10 mb-4 scroll-mt-20">
          <span class="w-8 h-8 rounded-lg bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-200 font-bold flex items-center justify-center text-sm">${sectionNumber}</span>
          <h2 dir="auto" class="text-lg sm:text-xl font-bold text-gray-900 dark:text-white">${titleHtml}</h2>
        </div>
      `);
      sectionNumber += 1;
      continue;
    }

    if (heading2Match) {
      closeList();
      const subtitleText = heading2Match[1].trim();
      htmlBlocks.push(`
        <h3 dir="auto" class="text-base sm:text-lg font-bold text-gray-900 dark:text-zinc-100 mt-6 mb-3 flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-blue-500"></span>
          ${parseInline(subtitleText)}
        </h3>
      `);
      continue;
    }

    if (heading3Match) {
      closeList();
      const subText = heading3Match[1].trim();
      htmlBlocks.push(`<h4 dir="auto" class="font-bold text-sm text-gray-900 dark:text-white mt-4 mb-2">${parseInline(subText)}</h4>`);
      continue;
    }

    if (line.startsWith('>') || line.startsWith('💡') || line.startsWith('نتیجه:')) {
      closeList();
      const cleanQuote = line.replace(/^[>💡\s]+/, '');
      htmlBlocks.push(`
        <div class="card-box p-4 sm:p-5 my-5 rounded-2xl border transition-all">
          <p dir="auto" class="!mb-0 text-sm sm:text-base leading-relaxed">
            ${parseInline(cleanQuote)}
          </p>
        </div>
      `);
      continue;
    }

    const listItemMatch = line.match(/^[-*•]\s+(.+)$/);
    const orderedItemMatch = line.match(/^[۰-۹0-9]+[-)]\s+(.+)$/);

    if (listItemMatch) {
      if (!inList || listType !== 'ul') {
        closeList();
        htmlBlocks.push('<ul class="space-y-2.5 pr-5 list-disc text-gray-700 dark:text-zinc-300 mb-5">');
        inList = true;
        listType = 'ul';
      }
      htmlBlocks.push(`<li dir="auto">${parseInline(listItemMatch[1])}</li>`);
      continue;
    }

    if (orderedItemMatch) {
      if (!inList || listType !== 'ol') {
        closeList();
        htmlBlocks.push('<ol class="space-y-2 pr-5 list-decimal text-gray-700 dark:text-zinc-300 mb-5">');
        inList = true;
        listType = 'ol';
      }
      htmlBlocks.push(`<li dir="auto">${parseInline(orderedItemMatch[1])}</li>`);
      continue;
    }

    closeList();
    htmlBlocks.push(`<p dir="auto">${parseInline(line)}</p>`);
  }

  closeList();

  return {
    contentHtml: htmlBlocks.join('\n'),
    toc,
    readTime: calculateReadTime(rawText),
  };
}
