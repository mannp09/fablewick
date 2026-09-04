import type { RamkabirBook } from '../data';
import type { StagePage } from '../reader/types';

// Ramkabir's own text isn't split into five pages the way Fablewick's
// is - `book.levels[level][lang]` is one string per paragraph, and a
// story runs 6 to 28 of them depending on level (verified against the
// live data: dry-banyan-twig kids has 11, the-foot-that-said-ram adults
// has 28). But there are always exactly five illustrations
// (`book.art.pages`), because that's what library/ramkabir-fablewick.html
// itself pairs with the text: five scenes placed at narrative fractions
// through however many paragraphs a level happens to have.
//
// This mirrors that exact placement so switching levels only ever swaps
// which strings sit inside a fixed five-page structure - the same page
// count, the same five pieces of art, every level, every language.
const FRACS = [0.15, 0.32, 0.54, 0.78];

function groupBoundaries(n: number): number[] {
  const bounds: number[] = [];
  let prev = 0;
  for (let k = 0; k < 4; k++) {
    const remaining = 4 - k; // groups still to place after this one
    const ideal = Math.round(FRACS[k] * n);
    const lo = prev + 1;
    const hi = n - remaining;
    const b = Math.max(lo, Math.min(hi, ideal));
    bounds.push(b);
    prev = b;
  }
  bounds.push(n);
  return bounds;
}

// Splits a level's paragraph list into exactly five groups. Every level
// measured so far has at least six paragraphs, comfortably above the
// five needed for one paragraph per group; the n <= 5 branch is a
// safety net rather than the common path, so a shorter future story
// never crashes the reader.
export function groupParagraphs(paragraphs: string[]): string[][] {
  const n = paragraphs.length;
  if (n === 0) return [[], [], [], [], []];
  if (n <= 5) {
    const groups: string[][] = paragraphs.map((p) => [p]);
    while (groups.length < 5) groups.push([]);
    return groups;
  }
  const bounds = groupBoundaries(n);
  const groups: string[][] = [];
  let start = 0;
  for (const b of bounds) {
    groups.push(paragraphs.slice(start, b));
    start = b;
  }
  return groups;
}

export function levelParagraphs(book: RamkabirBook, level: string, lang: string): string[] {
  const byLevel = book.levels[level] ?? book.levels[book.levelNames[0]] ?? {};
  return byLevel[lang] ?? byLevel.en ?? [];
}

const CONTENT_COUNT = 5;

export function buildHeritageStagePages(): StagePage[] {
  const pages: StagePage[] = [{ kind: 'cover', index: 0 }];
  for (let i = 0; i < CONTENT_COUNT; i++) pages.push({ kind: 'content', index: i });
  pages.push({ kind: 'end', index: 0 });
  return pages;
}

export function heritagePageTextFor(book: RamkabirBook, level: string, lang: string, pageIndex: number): string {
  const groups = groupParagraphs(levelParagraphs(book, level, lang));
  return (groups[pageIndex] ?? []).join('\n\n');
}

export function heritagePageArtUrl(book: RamkabirBook, pageIndex: number): string | undefined {
  return book.art.pages[pageIndex];
}
