// Typed loaders over the two JSON files scripts/sync-data.mjs writes.
// Nothing here re-derives a count by hand — every number a caller wants
// (book count, page count, language count) reads off the arrays these
// functions return.

import fablewickRaw from './fablewick.json';
import ramkabirRaw from './ramkabir.json';

export interface FablewickBookI18n {
  titles: Record<string, string>;
  kickers: Record<string, string>;
  covers: Record<string, string>;
  ends: Record<string, string>;
  endMarks: Record<string, string>;
  backLabels: Record<string, string>;
  endBtn: Record<string, string>;
  navPrev: Record<string, string>;
  navNext: Record<string, string>;
  pageLabel: Record<string, string>;
  pageTexts: Record<string, string[]>;
}

export interface FablewickBook {
  slug: string;
  title: string;
  author: string;
  ageRange: number[] | null;
  themes: string[];
  lesson: string;
  summary: string;
  languages: string[];
  pageCounts: Record<string, number>;
  i18n: FablewickBookI18n;
  art: {
    cover: string | null;
    pages: string[];
    coverTrim: string | null;
    coverTrim1600: string | null;
  };
}

export interface RamkabirBook {
  slug: string;
  color: string;
  scenes: string[];
  title: Record<string, string>;
  moral: Record<string, string>;
  languages: string[];
  levelNames: string[];
  levels: Record<string, Record<string, string[]>>;
  art: {
    cover: string | null;
    pages: string[];
    coverTrim: string | null;
    coverTrim1600: string | null;
  };
}

export const fablewickBooks: FablewickBook[] = fablewickRaw as FablewickBook[];
export const ramkabirBooks: RamkabirBook[] = ramkabirRaw as RamkabirBook[];

export function getFablewickBook(slug: string): FablewickBook | undefined {
  return fablewickBooks.find((b) => b.slug === slug);
}

export function getRamkabirBook(slug: string): RamkabirBook | undefined {
  return ramkabirBooks.find((b) => b.slug === slug);
}

// The full set of languages Fablewick ships in, derived from the union
// across every book rather than assumed to be the same five everywhere.
export function fablewickLanguages(): string[] {
  const set = new Set<string>();
  for (const book of fablewickBooks) {
    for (const lang of book.languages) set.add(lang);
  }
  return [...set].sort();
}

export function ramkabirLanguages(): string[] {
  const set = new Set<string>();
  for (const book of ramkabirBooks) {
    for (const lang of book.languages) set.add(lang);
  }
  return [...set].sort();
}
