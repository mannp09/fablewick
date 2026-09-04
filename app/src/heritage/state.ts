// Heritage-only persisted state. Language reuses the site-wide
// `fablewick.lang` key (src/context/LanguageContext.tsx / src/reader/
// constants.ts) so a choice carries across Fablewick and the Heritage
// Edition either direction - it's just clamped down to the three
// languages Ramkabir actually ships (en, hi, gu), never es or fr.
// Level is its own key: nothing else in the app has a concept of
// reading level, so it gets its own storage slot rather than piggy-
// backing on language.
export const HERITAGE_LANGUAGES = ['en', 'hi', 'gu'] as const;
export type HeritageLanguage = (typeof HERITAGE_LANGUAGES)[number];

const LANG_STORAGE_KEY = 'fablewick.lang';
const LEVEL_STORAGE_KEY = 'ramkabir.level';

export function readHeritageLanguage(): HeritageLanguage {
  try {
    const saved = window.localStorage.getItem(LANG_STORAGE_KEY);
    if (saved && (HERITAGE_LANGUAGES as readonly string[]).includes(saved)) {
      return saved as HeritageLanguage;
    }
  } catch {
    // localStorage unavailable - default below still renders fine.
  }
  return 'en';
}

export function storeHeritageLanguage(lang: string): void {
  try {
    window.localStorage.setItem(LANG_STORAGE_KEY, lang);
  } catch {
    // ignore - the choice still works for the rest of this session
  }
}

export function readHeritageLevel(levelNames: string[]): string {
  const fallback = levelNames.includes('kids') ? 'kids' : (levelNames[0] ?? 'kids');
  try {
    const saved = window.localStorage.getItem(LEVEL_STORAGE_KEY);
    return saved && levelNames.includes(saved) ? saved : fallback;
  } catch {
    return fallback;
  }
}

export function storeHeritageLevel(level: string): void {
  try {
    window.localStorage.setItem(LEVEL_STORAGE_KEY, level);
  } catch {
    // ignore
  }
}

// Its own prefix (not fablewick.progress.<slug>, src/reader/constants.ts)
// so a Ramkabir slug can never collide with a Fablewick one even though
// today none do.
const PROGRESS_PREFIX = 'ramkabir.progress.';

export function readHeritageProgress(slug: string): number | null {
  try {
    const raw = window.localStorage.getItem(PROGRESS_PREFIX + slug);
    if (raw === null) return null;
    const n = Number(raw);
    return Number.isInteger(n) && n >= 0 ? n : null;
  } catch {
    return null;
  }
}

export function writeHeritageProgress(slug: string, stageIndex: number): void {
  try {
    window.localStorage.setItem(PROGRESS_PREFIX + slug, String(stageIndex));
  } catch {
    // ignore
  }
}
