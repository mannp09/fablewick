import { useEffect, useState, type MouseEvent } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { LANGUAGES, useLanguage } from '../context/LanguageContext';
import './Header.css';

// Static file, synced by scripts/sync-data.mjs from the repo's src/assets/
// into public/brand/, so it is referenced by URL rather than imported.
const markUrl = '/fablewick/brand/fablewick-mark.png';

const LINKS = [
  { to: '/', label: 'Library', end: true },
  { to: '/heritage', label: 'Heritage', end: false },
  { to: '/#about', label: 'About', end: false, isAbout: true },
];

// The five site languages narrow per route: the Heritage edition only
// ever shipped en/hi/gu (see docs/v2-plan-2026-09-04.md, Rulings ->
// Levels), so its pages (and its reader) offer just those three; the
// Fablewick reader has its own in-stage language control, so the header
// row would just be a second, redundant control there and is hidden;
// everywhere else (the library) offers all five.
const HERITAGE_CODES = new Set(['en', 'hi', 'gu']);

export default function Header() {
  const { lang, setLang } = useLanguage();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  const isReaderRoute = location.pathname.startsWith('/read/');
  const isHeritageRoute = location.pathname.startsWith('/heritage');
  const visibleLanguages = isReaderRoute
    ? []
    : isHeritageRoute
      ? LANGUAGES.filter((l) => HERITAGE_CODES.has(l.code))
      : LANGUAGES;

  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setMenuOpen(false);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  const goToAbout = (e: MouseEvent) => {
    if (location.pathname === '/') {
      e.preventDefault();
      document.getElementById('about')?.scrollIntoView({ behavior: 'smooth' });
    }
    setMenuOpen(false);
  };

  const renderLinks = (onClick?: () => void) =>
    LINKS.map((link) =>
      link.isAbout ? (
        <a key={link.to} href={link.to} onClick={goToAbout} className={location.hash === '#about' ? 'active' : ''}>
          {link.label}
        </a>
      ) : (
        <NavLink
          key={link.to}
          to={link.to}
          end={link.end}
          onClick={onClick}
          className={({ isActive }) => (isActive ? 'active' : '')}
        >
          {link.label}
        </NavLink>
      ),
    );

  return (
    <header className="site-header">
      <div className="site-header-inner">
        <NavLink to="/" className="mark" end>
          <img className="mark-glyph" src={markUrl} alt="" width={28} height={28} />
          Fablewick
        </NavLink>

        <nav className="site-nav" aria-label="Primary">
          {renderLinks()}
        </nav>

        {visibleLanguages.length > 0 && (
          <div className="lang-chips" role="group" aria-label="Story language">
            {visibleLanguages.map((l) => (
              <button
                key={l.code}
                type="button"
                className="lang-chip"
                aria-pressed={l.code === lang}
                onClick={() => setLang(l.code)}
              >
                {l.short}
              </button>
            ))}
          </div>
        )}

        <button
          className="menu-toggle"
          type="button"
          aria-label="Toggle menu"
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen((v) => !v)}
        >
          <span />
        </button>
      </div>

      {menuOpen && (
        <div className="menu-sheet">
          <nav className="menu-sheet-nav" aria-label="Primary, mobile">
            {renderLinks(() => setMenuOpen(false))}
          </nav>
          {visibleLanguages.length > 0 && (
            <div className="menu-sheet-langs" role="group" aria-label="Story language">
              {visibleLanguages.map((l) => (
                <button
                  key={l.code}
                  type="button"
                  className="lang-chip"
                  aria-pressed={l.code === lang}
                  onClick={() => setLang(l.code)}
                >
                  {l.label}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </header>
  );
}
