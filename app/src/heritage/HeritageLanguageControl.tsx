import { useEffect, useRef, useState } from 'react';
import { READER_LANGUAGES } from '../reader/constants';
import { HERITAGE_LANGUAGES } from './state';

interface HeritageLanguageControlProps {
  lang: string;
  onChange: (lang: string) => void;
}

// The reader's own LanguageControl (src/reader/LanguageControl.tsx)
// always offers all five Fablewick languages - Ramkabir ships only
// three (en, hi, gu), so this is its own small component rather than a
// prop threaded into a file wave 3 owns. Same markup and class names
// (reader-lang, reader-lang-btn, reader-lang-menu, reader-lang-option)
// so it inherits Reader.css's styling exactly, just filtered down to
// the three languages that actually have Ramkabir text.
const OPTIONS = READER_LANGUAGES.filter((l) => (HERITAGE_LANGUAGES as readonly string[]).includes(l.code));

export default function HeritageLanguageControl({ lang, onChange }: HeritageLanguageControlProps) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const current = OPTIONS.find((l) => l.code === lang) ?? OPTIONS[0];

  useEffect(() => {
    if (!open) return;
    const onDocPointer = (e: PointerEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false);
    };
    document.addEventListener('pointerdown', onDocPointer);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('pointerdown', onDocPointer);
      document.removeEventListener('keydown', onKey);
    };
  }, [open]);

  return (
    <div className="reader-lang" ref={rootRef}>
      <button
        type="button"
        className="reader-icon-btn reader-lang-btn"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-label={`Story language, currently ${current.name}`}
        onClick={() => setOpen((v) => !v)}
      >
        {current.label}
      </button>
      {open && (
        <ul className="reader-lang-menu" role="listbox" aria-label="Choose a language">
          {OPTIONS.map((l) => (
            <li key={l.code}>
              <button
                type="button"
                role="option"
                aria-selected={l.code === lang}
                className={`reader-lang-option${l.code === lang ? ' active' : ''}`}
                onClick={() => {
                  onChange(l.code);
                  setOpen(false);
                }}
              >
                {l.name}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
