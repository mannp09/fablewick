// Small, hand-verified subset of the UI strings object already shipping
// inside library/ramkabir-fablewick.html (the const UI = {...} literal),
// copied verbatim rather than retyped from memory (T0-N). That file has
// no navPrev/navNext/end-mark concept - it's a single scrolling page,
// never paginated - so those three are new UI chrome, kept in English
// only, matching how components/Header.tsx already leaves its own nav
// labels (Library / Heritage / About) untranslated regardless of the
// site language.
export const HERITAGE_LEVEL_LABELS: Record<string, Record<string, string>> = {
  en: { kids: 'Kids', adults: 'Adults', seniors: 'Seniors' },
  gu: { kids: 'બાળકો', adults: 'પુખ્ત', seniors: 'વડીલો' },
  hi: { kids: 'बच्चे', adults: 'वयस्क', seniors: 'बुज़ुर्ग' },
};

export const HERITAGE_BACK_LABEL: Record<string, string> = {
  en: 'Library',
  gu: 'પુસ્તકાલય',
  hi: 'पुस्तकालय',
};

export function heritageLevelLabel(lang: string, level: string): string {
  return HERITAGE_LEVEL_LABELS[lang]?.[level] ?? HERITAGE_LEVEL_LABELS.en[level] ?? level;
}
