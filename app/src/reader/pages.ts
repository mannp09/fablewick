import type { FablewickBook } from '../data';
import type { StagePage } from './types';

// Content-page count for a given language, falling back to English, then
// to the art folder's own page count if the language is somehow absent
// from pageCounts entirely - never a hand-typed number.
export function contentCountFor(book: FablewickBook, lang: string): number {
  return book.pageCounts[lang] ?? book.pageCounts.en ?? book.art.pages.length;
}

export function buildStagePages(book: FablewickBook, lang: string): StagePage[] {
  const count = contentCountFor(book, lang);
  const pages: StagePage[] = [{ kind: 'cover', index: 0 }];
  for (let i = 0; i < count; i++) pages.push({ kind: 'content', index: i });
  pages.push({ kind: 'end', index: 0 });
  return pages;
}

// The cover art is served at .../cover.jpg by sync-data.mjs. A later wave
// wires the trimmed 1600x900 crop in as cover-trim.jpg alongside it; until
// that copy exists, the <img>'s onError in Reader.tsx falls back to the
// plain cover. Deriving the trimmed path from the real one (rather than
// rebuilding the /fablewick/art/... prefix by hand) means this keeps
// working if the base path ever changes.
export function coverTrimUrl(cover: string): string {
  return cover.replace(/cover\.jpg$/, 'cover-trim.jpg');
}

export function pageArtUrl(book: FablewickBook, contentIndex: number): string | undefined {
  return book.art.pages[contentIndex];
}

export function pageTextFor(book: FablewickBook, lang: string, contentIndex: number): string {
  const texts = book.i18n.pageTexts[lang] ?? book.i18n.pageTexts.en ?? [];
  return texts[contentIndex] ?? '';
}

export function textToParagraphs(text: string): string[] {
  return text
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .filter(Boolean);
}
