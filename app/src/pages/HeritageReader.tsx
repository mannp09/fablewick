import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Button from '../components/Button';
import { ramkabirBooks, getRamkabirBook } from '../data';
import type { RamkabirBook } from '../data';
import Starfield from '../reader/Starfield';
import { textToParagraphs } from '../reader/pages';
import { useReadAloud } from '../reader/useReadAloud';
import { useFullscreen } from '../reader/useFullscreen';
import { useIdle } from '../reader/useIdle';
import { useSwipe } from '../reader/useSwipe';
import HeritageLanguageControl from '../heritage/HeritageLanguageControl';
import LevelControl from '../heritage/LevelControl';
import { buildHeritageStagePages, heritagePageArtUrl, heritagePageTextFor } from '../heritage/pages';
import { HERITAGE_BACK_LABEL } from '../heritage/i18n';
import {
  readHeritageLanguage,
  readHeritageLevel,
  readHeritageProgress,
  storeHeritageLanguage,
  storeHeritageLevel,
  writeHeritageProgress,
} from '../heritage/state';
import './Reader.css';
import './HeritageReader.css';

// The reader chrome (Prev / Next / end mark) has no source translation
// anywhere in ramkabir-fablewick.html - that page never paginates, it
// scrolls - so it stays in English, the same fallback strings Reader.tsx
// itself falls back to when a Fablewick book is missing an i18n field.
const END_MARK = '✦'; // the exact glyph library/ramkabir-fablewick.html uses for its own <div class="endmark">
const PREV_LABEL = 'Back';
const NEXT_LABEL = 'Next';

function nextBookAfter(book: RamkabirBook): RamkabirBook {
  const idx = ramkabirBooks.findIndex((b) => b.slug === book.slug);
  return ramkabirBooks[(idx + 1) % ramkabirBooks.length];
}

export default function HeritageReader() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const book = slug ? getRamkabirBook(slug) : undefined;

  const [lang, setLang] = useState<string>(() => readHeritageLanguage());
  const [level, setLevel] = useState(() => readHeritageLevel(book?.levelNames ?? ['kids']));
  const [pageIndex, setPageIndex] = useState(0);
  const [continueIndex, setContinueIndex] = useState<number | null>(() =>
    book ? readHeritageProgress(book.slug) : null,
  );

  useEffect(() => {
    if (!book) return;
    setPageIndex(0);
    setContinueIndex(readHeritageProgress(book.slug));
    setLevel((prev) => (book.levelNames.includes(prev) ? prev : readHeritageLevel(book.levelNames)));
  }, [book]);

  const stagePages = useMemo(() => buildHeritageStagePages(), []);
  const total = stagePages.length;
  const current = stagePages[pageIndex];

  const goTo = useCallback(
    (index: number) => setPageIndex(Math.max(0, Math.min(index, total - 1))),
    [total],
  );
  const next = useCallback(() => setPageIndex((i) => Math.min(i + 1, total - 1)), [total]);
  const prev = useCallback(() => setPageIndex((i) => Math.max(i - 1, 0)), [total]);

  const stageRef = useRef<HTMLDivElement>(null);
  const { isFullscreen, toggle: toggleFullscreen } = useFullscreen(stageRef);
  const chromeIdle = useIdle(isFullscreen);
  const swipe = useSwipe(next, prev);

  useEffect(() => {
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = prevOverflow;
    };
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight') {
        next();
        e.preventDefault();
      } else if (e.key === 'ArrowLeft') {
        prev();
        e.preventDefault();
      } else if (e.key === 'Escape') {
        if (document.fullscreenElement) void document.exitFullscreen();
        else navigate('/heritage');
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [next, prev, navigate]);

  // The five illustrations are level- and language-independent (the
  // same five images pair with every level's text), so this only ever
  // needs to preload by page index, not by level or language.
  useEffect(() => {
    if (!book) return;
    const upcoming = stagePages[pageIndex + 1];
    if (upcoming?.kind === 'content') {
      const url = heritagePageArtUrl(book, upcoming.index);
      if (url) {
        const img = new Image();
        img.src = url;
      }
    }
  }, [book, pageIndex, stagePages]);

  useEffect(() => {
    if (!book || !current) return;
    if (current.kind === 'content') writeHeritageProgress(book.slug, pageIndex);
  }, [book, current, pageIndex]);

  const handleLangChange = (code: string) => {
    setLang(code);
    storeHeritageLanguage(code);
  };

  const handleLevelChange = (nextLevel: string) => {
    setLevel(nextLevel);
    storeHeritageLevel(nextLevel);
    // The content-page count is fixed at five regardless of level, so
    // the current page index stays valid - only the text underneath it
    // changes, exactly as the ruling asks.
  };

  const title = book ? (book.title[lang] ?? book.title.en) : '';
  const moral = book ? (book.moral[lang] ?? book.moral.en ?? '') : '';
  const libraryLabel = HERITAGE_BACK_LABEL[lang] ?? HERITAGE_BACK_LABEL.en;

  const statusLabel = !current
    ? ''
    : current.kind === 'cover'
      ? 'Cover'
      : current.kind === 'end'
        ? END_MARK
        : `${current.index + 1} of 5`;

  const readAloudText =
    !book || !current
      ? ''
      : current.kind === 'content'
        ? heritagePageTextFor(book, level, lang, current.index).replace(/\s*\n+\s*/g, ' ')
        : current.kind === 'cover'
          ? `${title}. ${moral}`
          : moral;

  const readAloud = useReadAloud({ text: readAloudText, lang });

  if (!slug || !book) {
    return (
      <main className="reader-stage-empty">
        <div className="reader-empty-card">
          <h1>Story not found</h1>
          <p>Route: /heritage/read/{slug ?? ''}</p>
          <Button to="/heritage" variant="outline">
            Back to the Heritage Edition
          </Button>
        </div>
      </main>
    );
  }

  const nextBook = nextBookAfter(book);
  const nextBookTitle = nextBook.title[lang] ?? nextBook.title.en;
  const continueContentNumber =
    continueIndex !== null && stagePages[continueIndex]?.kind === 'content'
      ? stagePages[continueIndex].index + 1
      : null;

  const coverSrc = book.art.coverTrim ?? book.art.cover;
  const rawCoverSrc = book.art.cover;

  return (
    <div
      className={`reader-overlay${isFullscreen ? ' is-fullscreen' : ''}`}
      ref={stageRef}
      onPointerDown={swipe.onPointerDown}
      onPointerUp={swipe.onPointerUp}
    >
      <Starfield />

      <div className={`reader-topbar${isFullscreen && chromeIdle ? ' is-hidden' : ''}`}>
        <Button to="/heritage" variant="ghost" className="reader-back-link">
          <span aria-hidden="true">&#8592;</span> {libraryLabel}
        </Button>
        <div className="reader-topbar-title">{title}</div>
        <div className="reader-topbar-right">
          <span className="reader-page-counter">{statusLabel}</span>
          <LevelControl
            levelNames={book.levelNames}
            level={level}
            lang={lang}
            onChange={handleLevelChange}
            className="reader-topbar-levels"
          />
          <HeritageLanguageControl lang={lang} onChange={handleLangChange} />
          <button
            type="button"
            className="reader-icon-btn reader-fullscreen-btn"
            aria-pressed={isFullscreen}
            aria-label={isFullscreen ? 'Exit full screen' : 'Enter full screen'}
            onClick={toggleFullscreen}
          >
            {isFullscreen ? '⤤' : '⤢'}
          </button>
          <div className="reader-readaloud">
            <button
              type="button"
              className={`reader-icon-btn reader-readaloud-btn${readAloud.status === 'speaking' ? ' is-speaking' : ''}`}
              aria-label={
                readAloud.status === 'speaking'
                  ? 'Pause reading aloud'
                  : readAloud.status === 'paused'
                    ? 'Resume reading aloud'
                    : 'Read this page aloud'
              }
              disabled={!readAloud.hasVoice}
              title={!readAloud.hasVoice ? 'No voice for this language on this device' : undefined}
              onClick={readAloud.toggle}
            >
              {readAloud.status === 'speaking' ? '⏸' : '▶'}
            </button>
            {readAloud.status === 'speaking' && <span className="reader-speaking-dot" aria-hidden="true" />}
          </div>
        </div>
      </div>

      <div className="reader-page-stage">
        {current.kind === 'cover' && (
          <div key={`cover-${lang}`} className="reader-page reader-page-cover">
            <div className="reader-cover-art">
              {coverSrc && (
                <img
                  className="reader-cover-img"
                  src={coverSrc}
                  alt=""
                  onError={(e) => {
                    const img = e.currentTarget;
                    if (img.dataset.fallback || !rawCoverSrc) return;
                    img.dataset.fallback = '1';
                    img.src = rawCoverSrc;
                  }}
                />
              )}
            </div>
            <span className="heritage-kicker-tag">Heritage Edition</span>
            <h1 className="reader-cover-title">{title}</h1>
            <p className="reader-cover-line">{moral}</p>
            <div className="reader-cover-actions">
              <Button variant="filled" onClick={() => goTo(1)}>
                Begin the story
              </Button>
              {continueContentNumber !== null && continueIndex !== null && continueIndex > 0 && (
                <Button variant="outline" onClick={() => goTo(continueIndex)}>
                  Continue from page {continueContentNumber}
                </Button>
              )}
            </div>
          </div>
        )}

        {current.kind === 'content' && (
          <div key={`page-${current.index}-${level}-${lang}`} className="reader-page reader-page-content">
            <div className="reader-book">
              <div className="reader-art">
                <img src={heritagePageArtUrl(book, current.index)} alt="" />
              </div>
              <div className="reader-text">
                {textToParagraphs(heritagePageTextFor(book, level, lang, current.index)).map((p, i) => (
                  <p key={i}>{p}</p>
                ))}
              </div>
            </div>
          </div>
        )}

        {current.kind === 'end' && (
          <div key={`end-${lang}`} className="reader-page reader-page-end">
            <div className="reader-end-mark">{END_MARK}</div>
            <p className="reader-end-line">{moral}</p>
            <div className="reader-end-actions">
              <Button to="/heritage" variant="outline">
                Back to the Heritage Edition
              </Button>
              <Button to={`/heritage/read/${nextBook.slug}`} variant="filled">
                Next story: {nextBookTitle}
              </Button>
            </div>
          </div>
        )}
      </div>

      <div className={`reader-navbar${isFullscreen && chromeIdle ? ' is-hidden' : ''}`}>
        <button
          type="button"
          className="reader-nav-btn reader-nav-prev"
          disabled={pageIndex === 0}
          onClick={prev}
        >
          <span aria-hidden="true">&#8592;</span> {PREV_LABEL}
        </button>
        <div className="reader-nav-center">
          <span className="reader-dots">
            {stagePages.map((_, i) => (
              <button
                key={i}
                type="button"
                className={`reader-dot${i === pageIndex ? ' active' : ''}`}
                aria-label={`Go to page ${i + 1}`}
                aria-current={i === pageIndex}
                onClick={() => goTo(i)}
              />
            ))}
          </span>
          <span className="reader-page-label" aria-live="polite">
            {statusLabel}
          </span>
        </div>
        <button
          type="button"
          className="reader-nav-btn reader-nav-next"
          disabled={pageIndex === total - 1}
          onClick={next}
        >
          {NEXT_LABEL} <span aria-hidden="true">&#8594;</span>
        </button>
      </div>
    </div>
  );
}
