import { useEffect, useRef, useState } from 'react';
import { READER_LANGUAGES } from './constants';

interface LanguageControlProps {
  lang: string;
  onChange: (lang: string) => void;
}

// A compact button that opens a short dropdown of the five languages,
// rather than five chips across the top bar - the top bar already carries
// the back link, title, page counter, fullscreen and read-aloud buttons,
// and five more tap targets would crowd the 390px layout.
export default function LanguageControl({ lang, onChange }: LanguageControlProps) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const current = READER_LANGUAGES.find((l) => l.code === lang) ?? READER_LANGUAGES[0];

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
          {READER_LANGUAGES.map((l) => (
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
