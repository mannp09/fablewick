import { Link } from 'react-router-dom';
import { useState } from 'react';
import Section from '../components/Section';
import Reveal from '../components/Reveal';
import { ramkabirBooks } from '../data';
import Starfield from '../reader/Starfield';
import LevelControl from '../heritage/LevelControl';
import { heritageLevelLabel } from '../heritage/i18n';
import { HERITAGE_LANGUAGES, readHeritageLanguage, readHeritageLevel, storeHeritageLanguage, storeHeritageLevel } from '../heritage/state';
import './Reader.css';
import './Library.css';
import './Heritage.css';

const HERITAGE_LANG_NAMES: Record<string, string> = { en: 'English', hi: 'हिंदी', gu: 'ગુજરાતી' };

const LEVEL_NAMES = ['kids', 'adults', 'seniors'];

// The synced data (src/data/ramkabir.json, from the story sources under
// library/) carries each book's levelNames in the order the source
// object happens to declare them - adults, kids, seniors - not the
// reading-age order a person expects on a chip row. Sort display copies
// to LEVEL_NAMES's order rather than touching the data file itself.
function orderedLevelNames(levelNames: string[]): string[] {
  return LEVEL_NAMES.filter((l) => levelNames.includes(l));
}

export default function Heritage() {
  const [lang, setLang] = useState<string>(() => readHeritageLanguage());
  const [level, setLevel] = useState(() => readHeritageLevel(LEVEL_NAMES));

  const handleLangChange = (code: string) => {
    setLang(code);
    storeHeritageLanguage(code);
  };
  const handleLevelChange = (next: string) => {
    setLevel(next);
    storeHeritageLevel(next);
  };

  return (
    <main className="library-page">
      <section className="hero hero-heritage">
        <Starfield />
        <div className="hero-inner">
          <span className="heritage-kicker-tag">Heritage Edition</span>
          <h1 className="heritage-hero-title">Ramkabir</h1>
          <p className="hero-tagline">Five stories from the Ram and Kabir tradition, in three reading levels.</p>

          <div className="heritage-controls-row">
            <div className="hero-langs" role="group" aria-label="Story language">
              {HERITAGE_LANGUAGES.map((code) => (
                <button
                  key={code}
                  type="button"
                  className="hero-lang-chip"
                  aria-pressed={code === lang}
                  onClick={() => handleLangChange(code)}
                >
                  {HERITAGE_LANG_NAMES[code]}
                </button>
              ))}
            </div>
            <LevelControl
              levelNames={LEVEL_NAMES}
              level={level}
              lang={lang}
              onChange={handleLevelChange}
              className="heritage-hero-levels"
            />
          </div>

          <Link className="heritage-back-link" to="/">
            <span aria-hidden="true">&#8592;</span> Back to Fablewick
          </Link>
        </div>
      </section>

      <Section id="stories">
        <div className="card-grid">
          {ramkabirBooks.map((book) => {
            const title = book.title[lang] ?? book.title.en;
            const moral = book.moral[lang] ?? book.moral.en;
            const cover = book.art.coverTrim ?? book.art.cover;
            return (
              <Reveal key={book.slug}>
                <Link className="book-card" to={`/heritage/read/${book.slug}`}>
                  <div className="book-card-media">
                    {cover && <img src={cover} alt="" loading="lazy" />}
                    <span className="age-chip">{book.levelNames.length} levels</span>
                  </div>
                  <div className="book-card-body">
                    <h3 className="book-card-title">{title}</h3>
                    <p className="book-card-lesson">{moral}</p>
                    <ul className="book-card-tags">
                      {orderedLevelNames(book.levelNames).map((l) => (
                        <li key={l} className="chip">
                          {heritageLevelLabel(lang, l)}
                        </li>
                      ))}
                    </ul>
                    <span className="btn btn-filled book-card-cta">
                      Read story
                      <span className="cta-arrow" aria-hidden="true">
                        →
                      </span>
                    </span>
                  </div>
                </Link>
              </Reveal>
            );
          })}
        </div>
      </Section>

      <Section id="about-heritage" title="About this edition">
        <Reveal>
          <div className="heritage-about">
            <p className="about-line">
              A visual retelling of five stories from the Ram and Kabir tradition, in three reading levels for
              kids, adults, and seniors.
            </p>
            <p className="about-line">
              Source material:{' '}
              <a href="https://ramkabir.org" target="_blank" rel="noopener">
                Ramkabir.org
              </a>{' '}
              and{' '}
              <a href="https://www.njbhagatsamaj.org" target="_blank" rel="noopener">
                NJ Bhagat Samaj
              </a>
              .
            </p>
            <p className="about-line">Authored by Mann Patel. Part of Fablewick.</p>
          </div>
        </Reveal>
      </Section>

      <footer className="site-footer">
        <p>Fablewick is made with love. © {new Date().getFullYear()}</p>
      </footer>
    </main>
  );
}
