import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';

// The five languages Fablewick ships in (per docs/v2-plan-2026-09-04.md,
// Rulings: "Fablewick stays languages only, en, hi, gu, es, fr"). Each
// name is written in its own script, not transliterated, so the chip
// itself is proof the language is really there.
export const LANGUAGES = [
  { code: 'en', label: 'English', short: 'EN' },
  { code: 'hi', label: 'हिन्दी', short: 'HI' },
  { code: 'gu', label: 'ગુજરાતી', short: 'GU' },
  { code: 'es', label: 'Español', short: 'ES' },
  { code: 'fr', label: 'Français', short: 'FR' },
] as const;

export type LanguageCode = (typeof LANGUAGES)[number]['code'];

// Shared with the reader (src/reader/constants.ts: LANG_STORAGE_KEY) so a
// language chosen on either the library page or inside a story carries
// over to the other, through the one localStorage key both read and
// write.
const STORAGE_KEY = 'fablewick.lang';

function readStoredLanguage(): LanguageCode {
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored && LANGUAGES.some((l) => l.code === stored)) return stored as LanguageCode;
  } catch {
    // localStorage unavailable (private mode, etc). Fall through to default.
  }
  return 'en';
}

interface LanguageContextValue {
  lang: LanguageCode;
  setLang: (code: LanguageCode) => void;
}

const LanguageContext = createContext<LanguageContextValue | undefined>(undefined);

// Site-wide language: card blurbs read it now, the readers read it once
// wave 3 wires them up. Persisted so a returning visitor keeps their
// language across a reload.
export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<LanguageCode>(() => readStoredLanguage());

  useEffect(() => {
    try {
      window.localStorage.setItem(STORAGE_KEY, lang);
    } catch {
      // ignore write failures, the in-memory state still works this session
    }
  }, [lang]);

  const value = useMemo(() => ({ lang, setLang: setLangState }), [lang]);

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage(): LanguageContextValue {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error('useLanguage must be used inside a LanguageProvider');
  return ctx;
}
