import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Button from '../components/Button';
import { fablewickBooks, getFablewickBook } from '../data';
import type { FablewickBook } from '../data';
import LanguageControl from '../reader/LanguageControl';
import Starfield from '../reader/Starfield';
import {
  buildStagePages,
  contentCountFor,
  coverTrimUrl,
  pageArtUrl,
  pageTextFor,
  textToParagraphs,
} from '../reader/pages';
import {
  nextStoryLabel,
  readProgress,
  readStoredLanguage,
  storeLanguage,
  stripChromeDecoration,
  writeProgress,
} from '../reader/constants';
import { useReadAloud } from '../reader/useReadAloud';
import { useFullscreen } from '../reader/useFullscreen';
import { useIdle } from '../reader/useIdle';
import { useSwipe } from '../reader/useSwipe';
import './Reader.css';

function nextBookAfter(book: FablewickBook): FablewickBook {
  const idx = fablewickBooks.findIndex((b) => b.slug === book.slug);
  return fablewickBooks[(idx + 1) % fablewickBooks.length];
}

export default function Reader() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const book = slug ? getFablewickBook(slug) : undefined;

  const [lang, setLang] = useState(() => readStoredLanguage(book?.languages ?? ['en']));
  const [pageIndex, setPageIndex] = useState(0);
  const [continueIndex, setContinueIndex] = useState<number | null>(() =>
    book ? readProgress(book.slug) : null,
  );

  // react-router keeps this same component mounted across a /read/:slug
  // change (e.g. the "Next story" link), so a fresh book needs its own
  // reset rather than relying on state initializers that only run once.
  useEffect(() => {
    if (!book) return;
    setPageIndex(0);
    setContinueIndex(readProgress(book.slug));
  }, [book]);

  const stagePages = useMemo(
    () => (book ? buildStagePages(book, lang) : []),
    [book, lang],
  );
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

  // Lock the page behind this fixed, full-viewport stage while it's open
  // so the sticky site header underneath never becomes scrollable into
  // view - the stage covers it, and body scroll would only expose a gap.
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
        else navigate('/');
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [next, prev, navigate]);

  // Preload the next content page's art so the crossfade never waits on
  // a network fetch mid-turn.
  useEffect(() => {
    if (!book) return;
    const upcoming = stagePages[pageIndex + 1];
    if (upcoming?.kind === 'content') {
      const url = pageArtUrl(book, upcoming.index);
      if (url) {
        const img = new Image();
        img.src = url;
      }
    }
  }, [book, pageIndex, stagePages]);

  useEffect(() => {
    if (!book || !current) return;
    if (current.kind === 'content') writeProgress(book.slug, pageIndex);
  }, [book, current, pageIndex]);

  const handleLangChange = (code: string) => {
    setLang(code);
    storeLanguage(code);
  };

  const title = book ? (book.i18n.titles[lang] ?? book.title) : '';
  const coverLine = book ? (book.i18n.covers[lang] ?? book.i18n.covers.en ?? '') : '';
  const endLine = book ? (book.i18n.ends[lang] ?? book.i18n.ends.en ?? '') : '';
  const endMark = book
    ? stripChromeDecoration(book.i18n.endMarks[lang] ?? book.i18n.endMarks.en ?? 'The End')
    : '';
  const prevLabel = book
    ? stripChromeDecoration(book.i18n.navPrev[lang] ?? book.i18n.navPrev.en ?? 'Back')
    : 'Back';
  const nextLabel = book
    ? stripChromeDecoration(book.i18n.navNext[lang] ?? book.i18n.navNext.en ?? 'Next')
    : 'Next';
  const libraryLabel = book
    ? stripChromeDecoration(book.i18n.backLabels[lang] ?? book.i18n.backLabels.en ?? 'Library')
    : 'Library';
  const endBtnLabel = book
    ? stripChromeDecoration(book.i18n.endBtn[lang] ?? book.i18n.endBtn.en ?? 'Back to the library')
    : 'Back to the library';
  const contentCount = book ? contentCountFor(book, lang) : 0;

  const statusLabel = !current
    ? ''
    : current.kind === 'cover'
      ? 'Cover'
      : current.kind === 'end'
        ? endMark
        : `${current.index + 1} of ${contentCount}`;

  const readAloudText = !book || !current
    ? ''
    : current.kind === 'content'
      ? pageTextFor(book, lang, current.index).replace(/\s*\n+\s*/g, ' ')
      : current.kind === 'cover'
        ? `${title}. ${coverLine}`
        : endLine;

  const readAloud = useReadAloud({ text: readAloudText, lang });

  if (!slug || !book) {
    return (
      <main className="reader-stage-empty">
        <div className="reader-empty-card">
          <h1>Story not found</h1>
          <p>Route: /read/{slug ?? ''}</p>
          <Button to="/" variant="outline">
            Back to the library
          </Button>
        </div>
      </main>
    );
  }

  const nextBook = nextBookAfter(book);
  const nextBookTitle = nextBook.i18n.titles[lang] ?? nextBook.title;
  const continueContentNumber =
    continueIndex !== null && stagePages[continueIndex]?.kind === 'content'
      ? stagePages[continueIndex].index + 1
      : null;

  const coverSrc = book.art.cover;
  const coverTrimSrc = coverSrc ? coverTrimUrl(coverSrc) : undefined;
  // The end page composes the same trimmed cover, preferring the real
  // build-time coverTrim field (verified to exist by sync-data.mjs)
  // over the regex-derived guess the cover page falls back to.
  const endCoverSrc = book.art.coverTrim ?? coverSrc ?? undefined;

  return (
    <div
      className={`reader-overlay${isFullscreen ? ' is-fullscreen' : ''}`}
      ref={stageRef}
      onPointerDown={swipe.onPointerDown}
      onPointerUp={swipe.onPointerUp}
    >
      <Starfield />

      <div className={`reader-topbar${isFullscreen && chromeIdle ? ' is-hidden' : ''}`}>
        <Button to="/" variant="ghost" className="reader-back-link">
          <span aria-hidden="true">&#8592;</span> {libraryLabel}
        </Button>
        <div className="reader-topbar-title">{title}</div>
        <div className="reader-topbar-right">
          <span className="reader-page-counter">{statusLabel}</span>
          <LanguageControl lang={lang} onChange={handleLangChange} />
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
            {readAloud.status === 'speaking' && (
              <span className="reader-speaking-dot" aria-hidden="true" />
            )}
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
                  src={coverTrimSrc}
                  alt=""
                  onError={(e) => {
                    const img = e.currentTarget;
                    if (img.dataset.fallback) return;
                    img.dataset.fallback = '1';
                    img.src = coverSrc;
                  }}
                />
              )}
            </div>
            <h1 className="reader-cover-title">{title}</h1>
            <p className="reader-cover-line">{coverLine}</p>
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
          <div key={`page-${current.index}-${lang}`} className="reader-page reader-page-content">
            <div className="reader-book">
              <div className="reader-art">
                <img src={pageArtUrl(book, current.index)} alt="" />
              </div>
              <div className="reader-text">
                {textToParagraphs(pageTextFor(book, lang, current.index)).map((p, i) => (
                  <p key={i}>{p}</p>
                ))}
              </div>
            </div>
          </div>
        )}

        {current.kind === 'end' && (
          <div key={`end-${lang}`} className="reader-page reader-page-end">
            <div className="reader-end-mark">{endMark}</div>
            {endCoverSrc && (
              <div className="reader-end-art">
                <img
                  className="reader-end-img"
                  src={endCoverSrc}
                  alt=""
                  onError={(e) => {
                    const img = e.currentTarget;
                    if (img.dataset.fallback || !coverSrc || endCoverSrc === coverSrc) return;
                    img.dataset.fallback = '1';
                    img.src = coverSrc;
                  }}
                />
              </div>
            )}
            <p className="reader-end-line">{endLine}</p>
            <div className="reader-end-actions">
              <Button to="/" variant="outline">
                {endBtnLabel}
              </Button>
              <Button to={`/read/${nextBook.slug}`} variant="filled">
                {nextStoryLabel(lang)}: {nextBookTitle}
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
          <span aria-hidden="true">&#8592;</span> {prevLabel}
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
          {nextLabel} <span aria-hidden="true">&#8594;</span>
        </button>
      </div>
    </div>
  );
}
