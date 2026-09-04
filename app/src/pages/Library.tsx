import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import Section from '../components/Section';
import Reveal from '../components/Reveal';
import { fablewickBooks, ramkabirBooks } from '../data';
import { LANGUAGES, useLanguage } from '../context/LanguageContext';
import './Library.css';

// Both are plain static files synced by scripts/sync-data.mjs (the
// wordmark from the repo's src/assets/, the headshot from
// mann-landing-v3), not bundled modules, so they are referenced by their
// served URL rather than imported, matching how the art paths in
// src/data/*.json are already written.
const wordmarkUrl = '/fablewick/brand/fablewick-logo-light.png';
const headshotUrl = '/fablewick/headshot.jpg';

// The four SOP steps, verbatim from mann.rodeo's AI Storybook card
// (claude-workspace/1-Projects/mann-landing-v3/src/content.ts, the
// ai-storybook slug's `steps` array).
const SOP_STEPS = [
  { n: '01', title: 'Outline It', text: 'Write how the story goes. Short is fine. This part stays yours.' },
  { n: '02', title: 'Let AI Write It', text: 'Give the outline to a model and let it write the pages.' },
  {
    n: '03',
    title: 'Find The Style',
    text: 'Use a continuity keeping image tool, let it write a prompt per scene, then let it compile the pictures with the story.',
  },
  { n: '04', title: 'Put It Online', text: 'One file, one link, and it is shareable.' },
];

// A small subtle starfield, confined to the hero. Same twinkling
// 4-point spark used in library/fablewick-landing.html's dusk theme,
// just fewer of them and dimmer, since the plan asks to keep the stars
// but make them subtle. Skips entirely under prefers-reduced-motion.
function HeroStarfield() {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const count = 22;
    const spark =
      '<svg viewBox="0 0 24 24" width="100%" height="100%" aria-hidden="true"><path d="M12 0 L13.5 10.5 L24 12 L13.5 13.5 L12 24 L10.5 13.5 L0 12 L10.5 10.5 Z" fill="#FFF6E0"/></svg>';
    const stars: HTMLDivElement[] = [];
    for (let i = 0; i < count; i++) {
      const s = document.createElement('div');
      s.className = 'hero-star';
      const size = (2 + Math.random() * 4).toFixed(1);
      s.style.left = (Math.random() * 98).toFixed(1) + '%';
      s.style.top = (Math.random() * 92).toFixed(1) + '%';
      s.style.width = size + 'px';
      s.style.height = size + 'px';
      if (!reduced) {
        s.style.animation = `heroTwinkle ${(2.6 + Math.random() * 3).toFixed(2)}s ease-in-out ${(Math.random() * 5).toFixed(2)}s infinite`;
      }
      s.innerHTML = spark;
      node.appendChild(s);
      stars.push(s);
    }
    return () => {
      for (const s of stars) s.remove();
    };
  }, []);

  return <div className="hero-starfield" ref={ref} aria-hidden="true" />;
}

// A copyable Venmo/Zelle handle: shows the value, a small button flips
// to "Copied" for a moment after a successful clipboard write.
function SupportHandle({ label, value }: { label: string; value: string }) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      // clipboard unavailable, the value is still selectable as plain text
    }
  };

  return (
    <div className="support-row">
      <span className="support-label">{label}</span>
      <span className="support-chip">{value}</span>
      <button type="button" className="support-copy" onClick={copy}>
        {copied ? 'Copied' : 'Copy'}
      </button>
    </div>
  );
}

export default function Library() {
  const { lang, setLang } = useLanguage();
  const year = new Date().getFullYear();

  useEffect(() => {
    if (window.location.hash === '#about') {
      document.getElementById('about')?.scrollIntoView();
    }
  }, []);

  return (
    <main className="library-page">
      <section className="hero">
        <HeroStarfield />
        <div className="hero-inner">
          <img className="hero-wordmark" src={wordmarkUrl} alt="Fablewick" />
          <p className="hero-tagline">A free storybook library for curious kids</p>
          <div className="hero-langs" role="group" aria-label="Story language">
            {LANGUAGES.map((l) => (
              <button
                key={l.code}
                type="button"
                className="hero-lang-chip"
                aria-pressed={l.code === lang}
                onClick={() => setLang(l.code)}
              >
                {l.label}
              </button>
            ))}
          </div>
        </div>
      </section>

      <Section id="library">
        <div className="card-grid">
          {fablewickBooks.map((book) => {
            const title = book.i18n.titles[lang] ?? book.title;
            const blurb = book.i18n.covers[lang] ?? book.summary;
            const cover = book.art.coverTrim ?? book.art.cover;
            return (
              <Reveal key={book.slug}>
                <Link className="book-card" to={`/read/${book.slug}`}>
                  <div className="book-card-media">
                    {cover && <img src={cover} alt="" loading="lazy" />}
                    {book.ageRange && (
                      <span className="age-chip">
                        Ages {book.ageRange[0]} to {book.ageRange[1]}
                      </span>
                    )}
                  </div>
                  <div className="book-card-body">
                    <h3 className="book-card-title">{title}</h3>
                    <p className="book-card-summary">{blurb}</p>
                    {book.lesson && <p className="book-card-lesson">{book.lesson}</p>}
                    <ul className="book-card-tags">
                      {book.themes.map((t) => (
                        <li key={t} className="chip">
                          {t}
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

        <Reveal>
          {/* Not one big anchor any more (an <a> cannot nest another <a>,
              and each thumbnail below needs its own link to its Heritage
              reader) - the copy block is its own Link to /heritage, the
              strip is five separate Links to /heritage/read/<slug>. */}
          <div className="heritage-card">
            <Link className="heritage-card-copy" to="/heritage">
              <span className="heritage-kicker">Heritage Edition</span>
              <h3 className="heritage-title">Ramkabir</h3>
              <p className="heritage-line">
                Five stories from the Ram and Kabir tradition, told in three reading levels.
              </p>
              <span className="btn btn-filled heritage-cta">
                Open the Heritage Edition
                <span className="cta-arrow" aria-hidden="true">
                  →
                </span>
              </span>
            </Link>
            <div className="heritage-strip">
              {ramkabirBooks.map((book) => {
                const cover = book.art.coverTrim ?? book.art.cover;
                if (!cover) return null;
                return (
                  <Link key={book.slug} className="heritage-strip-item" to={`/heritage/read/${book.slug}`}>
                    <img src={cover} alt="" loading="lazy" />
                  </Link>
                );
              })}
            </div>
          </div>
        </Reveal>
      </Section>

      <Section id="about" title="About">
        <Reveal>
          <div className="about-grid">
            <img className="about-headshot" src={headshotUrl} alt="Mann Patel" />
            <div className="about-copy">
              <p className="about-name">Mann Patel</p>
              <p className="about-line">
                A story read to you by someone who loves you builds the room the rest of your life gets built
                around.
              </p>
              <p className="about-line">
                I wrote these with my AI stack. The stories come from people I love: Dada in his garden, Ba in
                her kitchen.
              </p>
              <p className="about-line">Fablewick is how any child, anywhere, gets that room too.</p>
              <a className="about-rodeo-link" href="https://mann.rodeo" target="_blank" rel="noopener">
                mann.rodeo →
              </a>
            </div>
          </div>

          <ol className="sop-strip">
            {SOP_STEPS.map((step) => (
              <li key={step.n} className="sop-step">
                <span className="sop-n">{step.n}</span>
                <span className="sop-title">{step.title}</span>
                <span className="sop-text">{step.text}</span>
              </li>
            ))}
          </ol>

          <p className="about-free-line">Free forever. No accounts. No ads.</p>

          <div className="support-block">
            <p className="support-heading">Support the library</p>
            <SupportHandle label="Venmo" value="@youngceltic18" />
            <SupportHandle label="Zelle" value="732-491-3448" />
          </div>
        </Reveal>
      </Section>

      <footer className="site-footer">
        <p>Fablewick is made with love. © {year}</p>
      </footer>
    </main>
  );
}
