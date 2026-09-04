#!/usr/bin/env node
// Reads the repo's real sources of truth (never retyped by hand) and
// writes two flat JSON files the app imports at build time, plus copies
// the art those files reference into public/. Runs before every dev and
// build (see package.json). Every count downstream (books, pages,
// languages) is measured HERE, once, from the data itself.
//
// Sources, per docs/v2-plan-2026-09-04.md:
//   Fablewick book meta   -> src/content/books/<slug>/meta.json
//   Fablewick story text  -> library/reader-<slug>.i18n.json
//   Fablewick art         -> src/assets/pages/<slug>/{cover,page-NN}.jpg
//   Ramkabir book data    -> const BOOKS = [...] in library/ramkabir-fablewick.html
//   Ramkabir art          -> library/assets/ramkabir/<slug>/{cover,page-N}.jpg
//   Trimmed covers        -> library/assets/covers-trimmed/<slug>[-800].jpg
//                            (heritage-<slug>[-800].jpg for Ramkabir)
//   Headshot              -> claude-workspace/1-Projects/mann-landing-v3/public/headshot.jpg

import { copyFileSync, existsSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const APP = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const REPO = path.resolve(APP, '..');
const DATA_DIR = path.join(APP, 'src/data');
const PUBLIC_ART = path.join(APP, 'public/art');

const HEADSHOT_SRC = path.resolve(
  REPO,
  '../../claude-workspace/1-Projects/mann-landing-v3/public/headshot.jpg',
);

const COVERS_TRIMMED = path.join(REPO, 'library/assets/covers-trimmed');

// Copies the wave-1b trimmed cover (card size, 800px wide) and the
// full-size 1600px version (for the reader, later) for one slug into
// destDir as cover-trim.jpg / cover-trim-1600.jpg. Returns whether the
// 800px card cover was found, since that is the one the library grid
// requires.
function copyTrimmedCover(sourceSlug, destDir) {
  const card = copyIfExists(
    path.join(COVERS_TRIMMED, `${sourceSlug}-800.jpg`),
    path.join(destDir, 'cover-trim.jpg'),
  );
  copyIfExists(path.join(COVERS_TRIMMED, `${sourceSlug}.jpg`), path.join(destDir, 'cover-trim-1600.jpg'));
  return card;
}

function readJson(p) {
  return JSON.parse(readFileSync(p, 'utf8'));
}

function writeJson(p, data) {
  mkdirSync(path.dirname(p), { recursive: true });
  writeFileSync(p, JSON.stringify(data, null, 2) + '\n');
}

function copyIfExists(src, dest) {
  if (!existsSync(src)) {
    console.warn(`sync-data: missing source, skipped: ${src}`);
    return false;
  }
  mkdirSync(path.dirname(dest), { recursive: true });
  copyFileSync(src, dest);
  return true;
}

// ---------------------------------------------------------------------
// 1. Fablewick — 11 books, one folder per slug under src/content/books/.
// ---------------------------------------------------------------------

const BOOKS_DIR = path.join(REPO, 'src/content/books');
const bookSlugs = readdirSync(BOOKS_DIR, { withFileTypes: true })
  .filter((e) => e.isDirectory())
  .map((e) => e.name)
  .sort();

const fablewickBooks = [];

for (const slug of bookSlugs) {
  const metaPath = path.join(BOOKS_DIR, slug, 'meta.json');
  if (!existsSync(metaPath)) {
    console.warn(`sync-data: no meta.json for ${slug}, skipped`);
    continue;
  }
  const meta = readJson(metaPath);

  const readerPath = path.join(REPO, 'library', `reader-${slug}.i18n.json`);
  if (!existsSync(readerPath)) {
    console.warn(`sync-data: no reader i18n for ${slug}, skipped`);
    continue;
  }
  const reader = readJson(readerPath);

  const languages = Object.keys(reader.pageTexts ?? {}).sort();
  const pageCounts = Object.fromEntries(
    languages.map((lang) => [lang, (reader.pageTexts[lang] ?? []).length]),
  );

  // Art: sourced from src/assets/pages/<slug>/, .jpg only (each page also
  // ships a .png sibling from the original render pass — the reader and
  // library both use the jpg).
  const artSrcDir = path.join(REPO, 'src/assets/pages', slug);
  const pageFiles = existsSync(artSrcDir)
    ? readdirSync(artSrcDir)
        .filter((f) => /^page-\d+\.jpg$/i.test(f))
        .sort()
    : [];

  const destDir = path.join(PUBLIC_ART, slug);
  mkdirSync(destDir, { recursive: true });
  let coverCopied = false;
  if (existsSync(path.join(artSrcDir, 'cover.jpg'))) {
    coverCopied = copyIfExists(path.join(artSrcDir, 'cover.jpg'), path.join(destDir, 'cover.jpg'));
  }
  for (const file of pageFiles) {
    copyIfExists(path.join(artSrcDir, file), path.join(destDir, file));
  }
  const coverTrimCopied = copyTrimmedCover(slug, destDir);

  fablewickBooks.push({
    slug,
    title: meta.title,
    author: meta.author ?? 'Fablewick',
    ageRange: meta.ageRange ?? null,
    themes: meta.themes ?? [],
    lesson: meta.lesson ?? '',
    summary: meta.summary ?? '',
    languages,
    pageCounts,
    i18n: {
      titles: reader.titles ?? {},
      kickers: reader.kickers ?? {},
      covers: reader.covers ?? {},
      ends: reader.ends ?? {},
      endMarks: reader.end_marks ?? {},
      backLabels: reader.back_labels ?? {},
      endBtn: reader.end_btn ?? {},
      navPrev: reader.nav_prev ?? {},
      navNext: reader.nav_next ?? {},
      pageLabel: reader.page_label ?? {},
      pageTexts: reader.pageTexts ?? {},
    },
    art: {
      cover: coverCopied ? `/fablewick/art/${slug}/cover.jpg` : null,
      pages: pageFiles.map((f) => `/fablewick/art/${slug}/${f}`),
      coverTrim: coverTrimCopied ? `/fablewick/art/${slug}/cover-trim.jpg` : null,
      coverTrim1600: coverTrimCopied ? `/fablewick/art/${slug}/cover-trim-1600.jpg` : null,
    },
  });
}

writeJson(path.join(DATA_DIR, 'fablewick.json'), fablewickBooks);

// ---------------------------------------------------------------------
// 2. Ramkabir / Heritage Edition — parsed out of the live BOOKS array in
//    library/ramkabir-fablewick.html. Parsed with JSON.parse after
//    slicing the literal out of the script tag, never eval'd.
// ---------------------------------------------------------------------

const ramkabirHtmlPath = path.join(REPO, 'library/ramkabir-fablewick.html');
const ramkabirHtml = readFileSync(ramkabirHtmlPath, 'utf8');
const booksMatch = ramkabirHtml.match(/const BOOKS = (\[[\s\S]*?\]);/);
if (!booksMatch) {
  throw new Error('sync-data: could not find "const BOOKS = [...]" in ramkabir-fablewick.html');
}
const rawRamkabirBooks = JSON.parse(booksMatch[1]);

const ramkabirBooks = rawRamkabirBooks.map((book) => {
  const languages = Object.keys(book.title ?? {}).sort();
  const levelNames = Object.keys(book.levels ?? {}).sort();

  const artSrcDir = path.join(REPO, 'library/assets/ramkabir', book.slug);
  const destDir = path.join(PUBLIC_ART, 'heritage', book.slug);
  mkdirSync(destDir, { recursive: true });

  let coverCopied = false;
  const coverBasename = book.img_cover ? path.basename(book.img_cover) : null;
  if (coverBasename) {
    coverCopied = copyIfExists(path.join(artSrcDir, coverBasename), path.join(destDir, coverBasename));
  }

  const pageBasenames = (book.img_pages ?? []).map((p) => path.basename(p));
  for (const file of pageBasenames) {
    copyIfExists(path.join(artSrcDir, file), path.join(destDir, file));
  }
  const coverTrimCopied = copyTrimmedCover(`heritage-${book.slug}`, destDir);

  return {
    slug: book.slug,
    color: book.color,
    scenes: book.scenes ?? [],
    title: book.title ?? {},
    moral: book.moral ?? {},
    languages,
    levelNames,
    levels: book.levels ?? {},
    art: {
      cover: coverCopied ? `/fablewick/art/heritage/${book.slug}/${coverBasename}` : null,
      pages: pageBasenames.map((f) => `/fablewick/art/heritage/${book.slug}/${f}`),
      coverTrim: coverTrimCopied ? `/fablewick/art/heritage/${book.slug}/cover-trim.jpg` : null,
      coverTrim1600: coverTrimCopied ? `/fablewick/art/heritage/${book.slug}/cover-trim-1600.jpg` : null,
    },
  };
});

writeJson(path.join(DATA_DIR, 'ramkabir.json'), ramkabirBooks);

// ---------------------------------------------------------------------
// 3. Headshot, for the About section (circular crop applied in CSS).
// ---------------------------------------------------------------------

copyIfExists(HEADSHOT_SRC, path.join(APP, 'public/headshot.jpg'));

// ---------------------------------------------------------------------
// 3b. Brand marks, for the header (icon-only mark) and the hero
//     (the light wordmark, made for the dusk background). Copied from
//     the repo's src/assets/, not the app's own src/, since the app has
//     no assets tree of its own.
// ---------------------------------------------------------------------

copyIfExists(path.join(REPO, 'src/assets/fablewick-mark.png'), path.join(APP, 'public/brand/fablewick-mark.png'));
copyIfExists(
  path.join(REPO, 'src/assets/fablewick-logo-light.png'),
  path.join(APP, 'public/brand/fablewick-logo-light.png'),
);

// ---------------------------------------------------------------------
// 4. Prune stale per-slug art folders — a book removed from the source
//    folders should not keep shipping its old images forever.
// ---------------------------------------------------------------------

const liveFablewickSlugs = new Set(fablewickBooks.map((b) => b.slug));
if (existsSync(PUBLIC_ART)) {
  for (const entry of readdirSync(PUBLIC_ART, { withFileTypes: true })) {
    if (!entry.isDirectory() || entry.name === 'heritage') continue;
    if (!liveFablewickSlugs.has(entry.name)) {
      rmSync(path.join(PUBLIC_ART, entry.name), { recursive: true, force: true });
      console.log(`sync-data: removed stale art folder: ${entry.name}`);
    }
  }
}
const liveRamkabirSlugs = new Set(ramkabirBooks.map((b) => b.slug));
const heritageArtDir = path.join(PUBLIC_ART, 'heritage');
if (existsSync(heritageArtDir)) {
  for (const entry of readdirSync(heritageArtDir, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    if (!liveRamkabirSlugs.has(entry.name)) {
      rmSync(path.join(heritageArtDir, entry.name), { recursive: true, force: true });
      console.log(`sync-data: removed stale heritage art folder: ${entry.name}`);
    }
  }
}

console.log(
  `sync-data: ${fablewickBooks.length} Fablewick books, ${ramkabirBooks.length} Ramkabir books written to ${path.relative(APP, DATA_DIR)}`,
);
