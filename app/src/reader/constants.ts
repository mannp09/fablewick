// Fablewick's five story languages, and the localStorage keys the reader
// shares with the library page. The library page sets fablewick.lang when
// its own language chips are used; the reader reads it on mount and writes
// it back whenever its own language control changes, so the choice carries
// across a visit either direction.
export const READER_LANGUAGES = [
  { code: 'en', label: 'EN', name: 'English' },
  { code: 'hi', label: 'HI', name: 'Hindi' },
  { code: 'gu', label: 'GU', name: 'Gujarati' },
  { code: 'es', label: 'ES', name: 'Spanish' },
  { code: 'fr', label: 'FR', name: 'French' },
] as const;

export type LanguageCode = (typeof READER_LANGUAGES)[number]['code'];

export const LANG_STORAGE_KEY = 'fablewick.lang';
export const PROGRESS_PREFIX = 'fablewick.progress.';

// The i18n "chrome" strings (nav labels, the back/library/end-of-book
// buttons, the "The End" mark) carry their own decorative arrow or em
// dash baked into the translated text. The reader draws its own single
// arrow icon and its own end-mark rule, so any arrow/dash the string
// brings is stripped here at render time - the JSON itself is never
// edited (it belongs to the text-reduction wave).
const CHROME_DECORATION = /^[\s←‹→›➜—–-]+|[\s←‹→›➜—–-]+$/g;
export function stripChromeDecoration(s: string): string {
  return s.replace(CHROME_DECORATION, '');
}

// "Next story:" localised per language - the reader's own chrome string,
// not part of a book's i18n JSON (which only carries story text/covers/
// ends), so it lives here as a small standalone dictionary.
const NEXT_STORY_LABEL: Record<string, string> = {
  en: 'Next story',
  hi: 'अगली कहानी',
  gu: 'આગલી વાર્તા',
  es: 'Siguiente historia',
  fr: 'Histoire suivante',
};
export function nextStoryLabel(lang: string): string {
  return NEXT_STORY_LABEL[lang] ?? NEXT_STORY_LABEL.en;
}

export function readStoredLanguage(supported: readonly string[]): string {
  try {
    const saved = window.localStorage.getItem(LANG_STORAGE_KEY);
    return saved && supported.includes(saved) ? saved : 'en';
  } catch {
    return 'en';
  }
}

export function storeLanguage(lang: string): void {
  try {
    window.localStorage.setItem(LANG_STORAGE_KEY, lang);
  } catch {
    // localStorage unavailable (private mode, disabled storage) - the
    // reader still works for the session, it just won't persist.
  }
}

export function readProgress(slug: string): number | null {
  try {
    const raw = window.localStorage.getItem(PROGRESS_PREFIX + slug);
    if (raw === null) return null;
    const n = Number(raw);
    return Number.isInteger(n) && n >= 0 ? n : null;
  } catch {
    return null;
  }
}

export function writeProgress(slug: string, stageIndex: number): void {
  try {
    window.localStorage.setItem(PROGRESS_PREFIX + slug, String(stageIndex));
  } catch {
    // ignore
  }
}
