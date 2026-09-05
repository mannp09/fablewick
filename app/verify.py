"""
Wave 1a scaffold verification. Serves dist/ on 127.0.0.1:8794 (mounted at
/fablewick/, matching vite.config.ts's base and how GitHub Pages will
actually serve it) and runs Playwright checks against every route:

  a. the route renders (page title present, no Playwright navigation error)
  b. no console errors fire while the route is open
  c. Fraunces, Lora and Outfit are all present in document.fonts once
     the webfont link finishes loading
  d. no horizontal scroll at 390px wide (documentElement.scrollWidth
     stays within the viewport)

Also screenshots every route at 1440x900 and 390x844 into _shots/ (same
routes and viewports as shots.py, so this is the one file to run for a
pass/fail plus the visual record together).

Modelled on mann-landing-v3's verify.py (claude-workspace/1-Projects/
mann-landing-v3/verify.py). Requires: pip install playwright &&
playwright install chromium.
"""
import http.server
import json
import socketserver
import subprocess
import sys
import threading
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

# The library page and the reader both print Hindi/Gujarati story text in
# check details (language-switch checks). Windows' default console
# codepage (cp1252) can't encode Devanagari/Gujarati, which crashes a
# plain print() - reconfigure stdout to UTF-8 once, up front, so any
# check() detail prints regardless of script.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
SHOTS = ROOT / "_shots"
PORT = 8794
BASE = f"http://127.0.0.1:{PORT}/fablewick/"
VIEWPORTS = {"desktop": (1440, 900), "mobile": (390, 844)}

ROUTES = {
    "library": "",
    "reader": "read/pip-and-the-lost-cloud",
    "heritage": "heritage",
    "heritage-reader": "heritage/read/dry-banyan-twig",
}

REQUIRED_FONTS = ["Manrope"]

# Mann's ruling 2026-09-04: one font, no italic anywhere, and the retired
# Google fonts must never come back - not even loaded and unused.
FORBIDDEN_FONTS = ["Fraunces", "Lora", "Outfit"]
FORBIDDEN_TEXT = ["Free forever", "No accounts"]

results = []


def settle_reveals(page, viewport_height):
    """Scroll-triggered content (Reveal, a fade-up on IntersectionObserver)
    never fires for anything below the fold unless the page is actually
    scrolled - a full-page screenshot does not scroll it into view on its
    own, it only stitches whatever has already rendered. Walk down the
    document a viewport-height at a time (half a viewport of overlap, so
    nothing between two steps skips the visible area entirely - a fixed
    step count broke this on the much taller mobile stack, whose full
    height is several viewports), waiting for each to settle, so every
    Reveal has passed through the viewport at least once before the real
    checks/screenshot below. Same technique mann-landing-v3's shots.py
    uses (scroll_into_view_if_needed per section before its full shot).
    """
    height = page.evaluate("document.documentElement.scrollHeight")
    step = max(viewport_height // 2, 1)
    y = 0
    while y < height:
        page.evaluate(f"window.scrollTo(0, {y})")
        page.wait_for_timeout(110)
        y += step
    page.evaluate(f"window.scrollTo(0, {height})")
    page.wait_for_timeout(110)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(200)


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f" - {detail}" if detail else ""))


def build():
    subprocess.run(["npm", "run", "build"], cwd=ROOT, check=True, shell=True)


def serve():
    # SPA fallback: react-router's BrowserRouter needs every client route
    # (/read/:slug etc.) to resolve to the same index.html on a direct
    # navigation, since dist/ only ever contains one HTML file. GitHub
    # Pages needs its own 404.html rewrite trick for this in production
    # (a "ship" wave concern); this local server just serves index.html
    # for anything that isn't a real file, so the checks below exercise
    # the app the way a client-side navigation would.
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(DIST), **kwargs)

        def translate_path(self, path):
            if path.startswith("/fablewick/"):
                path = path[len("/fablewick"):]
            elif path == "/fablewick":
                path = "/"
            translated = super().translate_path(path)
            if not Path(translated).is_file():
                return str(DIST / "index.html")
            return translated

        def log_message(self, *args):
            pass  # keep the check output readable

    class Server(socketserver.TCPServer):
        # Without this, a re-run right after a previous one can hit
        # WinError 10048 ("only one usage of each socket address") while
        # the prior socket sits in TIME_WAIT, even though nothing is
        # still listening on the port.
        allow_reuse_address = True

    httpd = Server(("127.0.0.1", PORT), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


def run_checks_and_shots():
    SHOTS.mkdir(exist_ok=True)
    files = []
    with sync_playwright() as p:
        browser = p.chromium.launch()

        for route_name, route_path in ROUTES.items():
            for viewport_name, (width, height) in VIEWPORTS.items():
                page = browser.new_page(viewport={"width": width, "height": height})
                console_errors = []
                page.on(
                    "console",
                    lambda msg: console_errors.append(msg.text) if msg.type == "error" else None,
                )
                page.on("pageerror", lambda exc: console_errors.append(str(exc)))

                nav_ok = True
                nav_detail = ""
                try:
                    page.goto(BASE + route_path, wait_until="networkidle", timeout=15000)
                except Exception as exc:  # noqa: BLE001 - report, don't crash the run
                    nav_ok = False
                    nav_detail = str(exc)
                check(f"{route_name}/{viewport_name}: route renders", nav_ok, nav_detail)

                if nav_ok:
                    page.wait_for_timeout(500)  # let webfonts settle
                    settle_reveals(page, height)

                    check(
                        f"{route_name}/{viewport_name}: no console errors",
                        len(console_errors) == 0,
                        "; ".join(console_errors[:3]),
                    )

                    try:
                        page.evaluate("document.fonts.ready")
                    except Exception:
                        pass
                    loaded_fonts = page.evaluate(
                        "() => Array.from(document.fonts).map((f) => f.family)"
                    )
                    missing = [
                        f for f in REQUIRED_FONTS
                        if not any(f in family for family in loaded_fonts)
                    ]
                    check(
                        f"{route_name}/{viewport_name}: fonts loaded ({', '.join(REQUIRED_FONTS)})",
                        len(missing) == 0,
                        f"missing: {missing}" if missing else "",
                    )

                    # Mann's ruling 2026-09-04: the retired Google fonts
                    # must never be in document.fonts, loaded or not -
                    # not just absent from the rendered text.
                    forbidden_present = [
                        f for f in FORBIDDEN_FONTS
                        if any(f in family for family in loaded_fonts)
                    ]
                    check(
                        f"{route_name}/{viewport_name}: document.fonts carries none of Fraunces/Lora/Outfit",
                        len(forbidden_present) == 0,
                        f"present: {forbidden_present}" if forbidden_present else "",
                    )

                    italic_count = page.evaluate(
                        "() => Array.from(document.querySelectorAll('*'))"
                        ".filter(el => getComputedStyle(el).fontStyle === 'italic').length"
                    )
                    check(
                        f"{route_name}/{viewport_name}: no element has computed font-style italic",
                        italic_count == 0,
                        f"italic_count={italic_count}",
                    )

                    visible_text = page.inner_text("body")
                    found_forbidden_text = [t for t in FORBIDDEN_TEXT if t in visible_text]
                    check(
                        f"{route_name}/{viewport_name}: no 'Free forever' / 'No accounts' text on the page",
                        len(found_forbidden_text) == 0,
                        f"found: {found_forbidden_text}" if found_forbidden_text else "",
                    )

                    if viewport_name == "mobile":
                        scroll_width = page.evaluate("document.documentElement.scrollWidth")
                        check(
                            f"{route_name}/{viewport_name}: no horizontal scroll at 390",
                            scroll_width <= width + 1,
                            f"scrollWidth={scroll_width}, viewport={width}",
                        )

                    path = SHOTS / f"{route_name}-{viewport_name}.png"
                    page.screenshot(path=str(path), full_page=True)
                    files.append(path)

                page.close()
        browser.close()
    return files


def check_library_page():
    """Wave-2 library page checks: the 11 book cards, the Heritage
    preview card, the About section content, and the language chip
    actually switching a card's blurb. Runs once at desktop width - these
    are content/wiring checks, not layout checks (those are covered per
    viewport above).
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(BASE, wait_until="networkidle", timeout=15000)
        page.wait_for_timeout(500)

        cards = page.locator(".book-card")
        check("library: 11 book cards present", cards.count() == 11, f"found {cards.count()}")

        cover_widths = page.eval_on_selector_all(
            ".book-card-media img", "els => els.map(e => e.naturalWidth)"
        )
        check(
            "library: every card cover image loaded (naturalWidth > 0)",
            len(cover_widths) == 11 and all(w > 0 for w in cover_widths),
            f"widths={cover_widths}",
        )

        hrefs = page.eval_on_selector_all(".book-card", "els => els.map(e => e.getAttribute('href'))")
        check(
            "library: every card links to /read/<slug>",
            all(h and h.startswith("/fablewick/read/") for h in hrefs),
            f"hrefs={hrefs}",
        )

        heritage_href = page.eval_on_selector(".heritage-card-copy", "el => el.getAttribute('href')")
        check(
            "library: Heritage card links to /heritage",
            heritage_href == "/fablewick/heritage",
            f"href={heritage_href}",
        )

        # wave-5 residual: the Heritage card's five thumbnails were too
        # small for the room they had, and weren't individually
        # clickable (the whole card was one <a>). Each one is now its
        # own link to its Heritage reader.
        strip_hrefs = page.eval_on_selector_all(
            ".heritage-strip-item", "els => els.map(e => e.getAttribute('href'))"
        )
        check(
            "library: Heritage strip has 5 links, each to /heritage/read/<slug>",
            len(strip_hrefs) == 5 and all(h and h.startswith("/fablewick/heritage/read/") for h in strip_hrefs),
            f"hrefs={strip_hrefs}",
        )

        about = page.locator("#about")
        check(
            "library: About has the headshot",
            about.locator(".about-headshot").count() == 1,
        )
        check(
            "library: About links to mann.rodeo",
            about.locator("a[href='https://mann.rodeo']").count() == 1,
        )
        check(
            "library: About has all 4 SOP steps",
            about.locator(".sop-step").count() == 4,
            f"found {about.locator('.sop-step').count()}",
        )
        support_text = about.locator(".support-block").inner_text()
        check(
            "library: About shows both support handles",
            "@youngceltic18" in support_text and "732-491-3448" in support_text,
            support_text,
        )

        # wave-5 residual: the Copy buttons sat at the row's far edge,
        # orphaned from the chip they copy. Each Copy button now sits
        # right after its chip - assert the gap is small, not "at the
        # end of a wide flex row" (which margin-left:auto used to do).
        gaps = page.eval_on_selector_all(
            ".support-row",
            "rows => rows.map(row => { "
            "const chip = row.querySelector('.support-chip'); "
            "const btn = row.querySelector('.support-copy'); "
            "if (!chip || !btn) return null; "
            "return btn.getBoundingClientRect().left - chip.getBoundingClientRect().right; })",
        )
        check(
            "library: every support row's Copy button sits within 24px of its chip",
            len(gaps) > 0 and all(g is not None and 0 <= g <= 24 for g in gaps),
            f"gaps={gaps}",
        )

        first_title_before = page.locator(".book-card-title").first.inner_text()
        page.get_by_role("button", name="हिन्दी").first.click()
        page.wait_for_timeout(200)
        first_title_after = page.locator(".book-card-title").first.inner_text()
        check(
            "library: Hindi language chip switches a card's title",
            first_title_after != first_title_before,
            f"before={first_title_before!r} after={first_title_after!r}",
        )

        page.close()
        browser.close()


# ── wave 6: About section contact buttons ──────────────────────────────


def check_about_actions():
    """Wave 6: the About section's underlined mann.rodeo text link is now
    a row of three Button components (mann.rodeo, Email, LinkedIn). Checks
    the row's shape and hrefs at desktop, that the raw email address never
    appears as visible page text at either viewport, and that the row
    collapses into a full-width vertical stack at 390px - measured
    against the copy column's own actual rendered width, since that
    column has no hardcoded width of its own.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()

        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(BASE, wait_until="networkidle", timeout=15000)
        page.wait_for_timeout(400)

        actions = page.locator("#about .about-actions")
        check("about-actions: row present", actions.count() == 1)

        children = actions.locator("> *")
        check(
            "about-actions: exactly 3 direct children",
            children.count() == 3,
            f"found {children.count()}",
        )

        # Wave "Email button" (2026-09-05): the Email action is now a real
        # <button> (copies the address, flips its own label, then opens
        # mail) rather than an <a href="mailto:...">, so this row is no
        # longer all-anchors - select both tags and check the middle one
        # by tag instead of by href.
        tags = page.eval_on_selector_all(
            "#about .about-actions > a, #about .about-actions > button",
            "els => els.map(e => ({tag: e.tagName, href: e.getAttribute('href')}))",
        )
        check(
            "about-actions: mann.rodeo anchor, Email button, linkedin anchor in order",
            len(tags) == 3
            and tags[0]["tag"] == "A"
            and tags[0]["href"].startswith("https://mann.rodeo")
            and tags[1]["tag"] == "BUTTON"
            and tags[2]["tag"] == "A"
            and tags[2]["href"].startswith("https://www.linkedin.com/"),
            f"tags={tags}",
        )

        min_heights = page.eval_on_selector_all(
            "#about .about-actions > a, #about .about-actions > button",
            "els => els.map(e => parseFloat(getComputedStyle(e).minHeight))",
        )
        check(
            "about-actions: every button's computed min-height is at least 44px",
            len(min_heights) == 3 and all(h >= 44 for h in min_heights),
            f"min_heights={min_heights}",
        )

        desktop_text = page.inner_text("body")
        check(
            "about-actions: the raw email never appears as visible page text (desktop)",
            "mann09patel@gmail.com" not in desktop_text,
        )

        # ---- Email button: copies to clipboard, flips its label, then
        # opens mail (intercepted via window.__openMail so the test page
        # never actually navigates) ----
        page.context.grant_permissions(["clipboard-read", "clipboard-write"])
        page.evaluate("() => { window.__openMail = (href) => { window.__lastMailHref = href; }; }")
        SHOTS.mkdir(exist_ok=True)
        page.screenshot(path=str(SHOTS / "wave-email-fablewick-before.png"))

        email_button = page.locator("#about .about-actions > button")
        email_button.click()
        label_after_click = None
        for _ in range(6):
            label_after_click = email_button.inner_text().strip()
            if label_after_click == "Copied":
                break
            page.wait_for_timeout(50)
        check(
            "Email button: label reads Copied within 300ms of the click",
            label_after_click == "Copied",
            f"label={label_after_click}",
        )

        clipboard_text = page.evaluate("() => navigator.clipboard.readText()")
        check(
            "Email button: clipboard holds the address after the click",
            clipboard_text == "mann09patel@gmail.com",
            f"clipboard={clipboard_text}",
        )

        mail_href = page.evaluate("() => window.__lastMailHref")
        check(
            "Email button: still opens mailto (intercepted) after the copy",
            mail_href == "mailto:mann09patel@gmail.com",
            f"mail_href={mail_href}",
        )

        text_after_click = page.inner_text("body")
        check(
            "about-actions: the raw email still never appears as visible page text after the click",
            "mann09patel@gmail.com" not in text_after_click,
        )

        page.wait_for_timeout(1000)
        page.screenshot(path=str(SHOTS / "wave-email-fablewick-after.png"))

        page.close()

        mobile = browser.new_page(viewport={"width": 390, "height": 844})
        mobile.goto(BASE, wait_until="networkidle", timeout=15000)
        mobile.wait_for_timeout(400)
        settle_reveals(mobile, 844)

        mobile_text = mobile.inner_text("body")
        check(
            "about-actions: the raw email never appears as visible page text (390px)",
            "mann09patel@gmail.com" not in mobile_text,
        )

        layout = mobile.evaluate(
            """() => {
                const copy = document.querySelector('#about .about-copy');
                const btns = Array.from(document.querySelectorAll('#about .about-actions > a, #about .about-actions > button'));
                const copyWidth = copy.getBoundingClientRect().width;
                const tops = btns.map(b => b.getBoundingClientRect().top);
                const widths = btns.map(b => b.getBoundingClientRect().width);
                const stacked = tops[0] < tops[1] && tops[1] < tops[2];
                return { copyWidth, widths, stacked };
            }"""
        )
        check(
            "about-actions: the 3 buttons stack vertically at 390px",
            layout["stacked"],
            f"layout={layout}",
        )
        check(
            "about-actions: each stacked button's width is within 4px of the copy column's width",
            len(layout["widths"]) == 3 and all(abs(w - layout["copyWidth"]) <= 4 for w in layout["widths"]),
            f"copyWidth={layout['copyWidth']} widths={layout['widths']}",
        )

        mobile.close()
        browser.close()


# ── wave 3: the reader (/read/:slug) ──────────────────────────────────
# Separate from run_checks_and_shots() above (which only ever loads a
# route's default, page-0 state): the reader has real interaction to
# verify - page turns, language switching, the responsive spread/stack
# layout swap - so it drives one page through several states rather
# than just loading and screenshotting it once.
READER_SLUG = "the-quiet-bear"


def reader_book_meta(slug):
    # Read straight from the synced data file rather than hand-typing
    # this book's page count - sync-data.mjs already measured it once.
    data = json.loads((ROOT / "src/data/fablewick.json").read_text(encoding="utf-8"))
    return next(b for b in data if b["slug"] == slug)


def grid_track_count(page, selector):
    # Passed as a JS function + arg (rather than interpolated into the
    # source string) so the selector never has to survive two rounds of
    # escaping - Python's f-string braces, then Playwright's own eval.
    return page.evaluate(
        """(sel) => {
            const el = document.querySelector(sel);
            if (!el) return 0;
            return getComputedStyle(el).gridTemplateColumns.trim().split(/\\s+/).length;
        }""",
        selector,
    )


def check_reader_page():
    SHOTS.mkdir(exist_ok=True)
    book = reader_book_meta(READER_SLUG)
    content_count = book["pageCounts"]["en"]
    expected_dots = content_count + 2  # cover + content pages + end

    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ── desktop pass: 1440x900 - spread layout, nav, language, controls
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: console_errors.append(str(exc)))

        page.goto(BASE + f"read/{READER_SLUG}", wait_until="networkidle", timeout=15000)
        page.wait_for_timeout(400)

        def counter_text():
            return page.evaluate(
                "document.querySelector('.reader-page-counter')?.textContent ?? ''"
            )

        cover_loaded = page.evaluate(
            "() => { const img = document.querySelector('.reader-cover-img'); "
            "return !!img && img.complete && img.naturalWidth > 0; }"
        )
        check("reader: page 0 shows the cover art loaded", cover_loaded)
        check("reader: cover counter reads 'Cover'", counter_text() == "Cover", counter_text())

        dots_count = page.evaluate("document.querySelectorAll('.reader-dot').length")
        check(
            "reader: dots count equals content pages plus cover and end",
            dots_count == expected_dots,
            f"dots={dots_count}, expected={expected_dots}",
        )

        page.screenshot(path=str(SHOTS / "reader-detail-cover-desktop.png"))

        page.click(".reader-nav-next")
        page.wait_for_timeout(350)
        check(
            "reader: Next advances the counter",
            counter_text() == f"1 of {content_count}",
            counter_text(),
        )

        page.keyboard.press("ArrowRight")
        page.wait_for_timeout(350)
        check(
            "reader: ArrowRight advances the counter",
            counter_text() == f"2 of {content_count}",
            counter_text(),
        )

        tracks_desktop = grid_track_count(page, ".reader-book")
        check(
            "reader: spread layout (two columns) active at 1440",
            tracks_desktop == 2,
            f"tracks={tracks_desktop}",
        )

        page.screenshot(path=str(SHOTS / "reader-detail-spread-desktop.png"))

        english_text = page.evaluate("document.querySelector('.reader-text')?.textContent ?? ''")
        page.click(".reader-lang-btn")
        page.wait_for_timeout(150)
        page.click("button.reader-lang-option:has-text('Hindi')")
        page.wait_for_timeout(300)
        hindi_text = page.evaluate("document.querySelector('.reader-text')?.textContent ?? ''")
        has_devanagari = page.evaluate(f"/[\\u0900-\\u097F]/.test({json.dumps(hindi_text)})")
        check(
            "reader: language control switches the page text (Hindi string appears)",
            has_devanagari and hindi_text != english_text,
            hindi_text[:40],
        )

        fullscreen_btn_count = page.evaluate(
            "document.querySelectorAll('.reader-fullscreen-btn').length"
        )
        check("reader: fullscreen button exists", fullscreen_btn_count == 1)

        # Chrome strings (nav labels, the library/back link) come from
        # per-book i18n JSON that already carries its own arrow/dash -
        # stripChromeDecoration() is supposed to strip it at render time
        # so the button never draws two arrows or a bare dash next to
        # the one arrow icon the UI itself always draws.
        arrow_chars = "←‹→›➜"
        nav_button_texts = {
            sel: page.evaluate(f"document.querySelector('{sel}')?.textContent ?? ''")
            for sel in (".reader-back-link", ".reader-nav-prev", ".reader-nav-next")
        }
        double_arrow = {
            sel: text
            for sel, text in nav_button_texts.items()
            if sum(1 for ch in text if ch in arrow_chars) > 1
        }
        check(
            "reader: no button text contains two arrows",
            len(double_arrow) == 0,
            f"{double_arrow}" if double_arrow else "",
        )

        dash_chars = "—–-"
        dash_edged = {
            sel: text
            for sel, text in nav_button_texts.items()
            if text.strip() and (text.strip()[0] in dash_chars or text.strip()[-1] in dash_chars)
        }
        check(
            "reader: no rendered chrome string starts or ends with a dash",
            len(dash_edged) == 0,
            f"{dash_edged}" if dash_edged else "",
        )

        # Playwright's bundled Chromium reports zero speechSynthesis
        # voices, so every language is a "no voice on this device" -
        # assert the disabled state and tooltip rather than a live speak.
        readaloud = page.locator(".reader-readaloud-btn")
        check("reader: read aloud button exists", readaloud.count() == 1)
        readaloud_disabled = readaloud.is_disabled()
        readaloud_title = readaloud.get_attribute("title") or ""
        check(
            "reader: read aloud disables with a tooltip when no voice exists (headless Chromium)",
            readaloud_disabled and "No voice for this language" in readaloud_title,
            f"disabled={readaloud_disabled}, title={readaloud_title}",
        )

        # Walk to the end page for a screenshot + a console-error check
        # over the whole interaction, not just the initial load. Clicks
        # until Next disables itself rather than a fixed count, since the
        # language switch above didn't move the page - we're already two
        # pages in, not back at the cover.
        next_btn = page.locator(".reader-nav-next")
        for _ in range(expected_dots + 1):
            if next_btn.is_disabled():
                break
            next_btn.click()
            page.wait_for_timeout(200)
        end_mark = page.evaluate("document.querySelector('.reader-end-mark')?.textContent ?? ''")
        check("reader: reaches the end page", len(end_mark) > 0, end_mark)

        end_counter = page.evaluate(
            "document.querySelector('.reader-page-counter')?.textContent ?? ''"
        )
        end_chrome = {"end mark": end_mark, "end page counter": end_counter}
        end_dash_edged = {
            label: text
            for label, text in end_chrome.items()
            if text.strip() and (text.strip()[0] in dash_chars or text.strip()[-1] in dash_chars)
        }
        check(
            "reader: end mark/counter carry no leading or trailing dash",
            len(end_dash_edged) == 0,
            f"{end_dash_edged}" if end_dash_edged else "",
        )

        end_img = page.evaluate(
            "() => { const img = document.querySelector('.reader-page-end img'); "
            "return !!img && img.complete && img.naturalWidth > 0; }"
        )
        check("reader: end page shows the cover image", end_img)

        page.screenshot(path=str(SHOTS / "reader-detail-end-desktop.png"))

        check(
            "reader/desktop interaction: no console errors",
            len(console_errors) == 0,
            "; ".join(console_errors[:3]),
        )
        page.close()

        # ── mobile pass: 390x844 - stacked layout, no horizontal scroll
        mobile = browser.new_page(viewport={"width": 390, "height": 844})
        mobile_errors = []
        mobile.on("console", lambda msg: mobile_errors.append(msg.text) if msg.type == "error" else None)
        mobile.on("pageerror", lambda exc: mobile_errors.append(str(exc)))

        mobile.goto(BASE + f"read/{READER_SLUG}", wait_until="networkidle", timeout=15000)
        mobile.wait_for_timeout(400)
        mobile.click(".reader-nav-next")
        mobile.wait_for_timeout(350)

        tracks_mobile = grid_track_count(mobile, ".reader-book")
        check(
            "reader: stacked layout (one column) active at 390",
            tracks_mobile == 1,
            f"tracks={tracks_mobile}",
        )

        scroll_width = mobile.evaluate("document.documentElement.scrollWidth")
        check(
            "reader/mobile: no horizontal scroll at 390",
            scroll_width <= 391,
            f"scrollWidth={scroll_width}",
        )

        mobile.screenshot(path=str(SHOTS / "reader-detail-content-mobile.png"))

        # Scroll the content panel all the way down and confirm the last
        # paragraph actually clears the nav bar - the thing that was
        # cutting "long, long time." off before the panel was made to
        # scroll (see the mobile-clipping fix in Reader.css).
        mobile.evaluate(
            "() => { const p = document.querySelector('.reader-page-content'); "
            "if (p) p.scrollTop = p.scrollHeight; }"
        )
        mobile.wait_for_timeout(150)
        last_para_bottom = mobile.evaluate(
            "() => { const ps = document.querySelectorAll('.reader-text p'); "
            "const last = ps[ps.length - 1]; "
            "return last ? last.getBoundingClientRect().bottom : null; }"
        )
        navbar_top_mobile = mobile.evaluate(
            "document.querySelector('.reader-navbar').getBoundingClientRect().top"
        )
        check(
            "reader/mobile: last paragraph is reachable above the nav bar",
            last_para_bottom is not None and last_para_bottom <= navbar_top_mobile + 1,
            f"paragraph bottom={last_para_bottom}, navbar top={navbar_top_mobile}",
        )

        check(
            "reader/mobile interaction: no console errors",
            len(mobile_errors) == 0,
            "; ".join(mobile_errors[:3]),
        )
        mobile.close()

        browser.close()


# ── wave 4: the Heritage Edition (/heritage, /heritage/read/:slug) ────
HERITAGE_READER_SLUG = "dry-banyan-twig"


def check_heritage_page():
    """/heritage: 5 story cards with loaded covers, and a level control
    with the three options (Kids/Adults/Seniors)."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(BASE + "heritage", wait_until="networkidle", timeout=15000)
        page.wait_for_timeout(500)

        cards = page.locator(".book-card")
        check("heritage: 5 story cards present", cards.count() == 5, f"found {cards.count()}")

        cover_widths = page.eval_on_selector_all(
            ".book-card-media img", "els => els.map(e => e.naturalWidth)"
        )
        check(
            "heritage: every card cover image loaded (naturalWidth > 0)",
            len(cover_widths) == 5 and all(w > 0 for w in cover_widths),
            f"widths={cover_widths}",
        )

        hrefs = page.eval_on_selector_all(".book-card", "els => els.map(e => e.getAttribute('href'))")
        check(
            "heritage: every card links to /heritage/read/<slug>",
            all(h and h.startswith("/fablewick/heritage/read/") for h in hrefs),
            f"hrefs={hrefs}",
        )

        level_buttons = page.locator(".heritage-hero-levels .heritage-level-btn")
        check(
            "heritage: level control shows 3 options",
            level_buttons.count() == 3,
            f"found {level_buttons.count()}",
        )

        # wave-5 residual: the data's levelNames are ordered adults, kids,
        # seniors (the source object's own order); the cards should read
        # Kids, Adults, Seniors like a reading-age ladder.
        first_card_level_chips = page.locator(".book-card").first.locator(".book-card-tags .chip").all_text_contents()
        check(
            "heritage: first card's level chips start with Kids",
            len(first_card_level_chips) > 0 and first_card_level_chips[0] == "Kids",
            f"chips={first_card_level_chips}",
        )

        back_link_href = page.eval_on_selector(".heritage-back-link", "el => el.getAttribute('href')")
        check(
            "heritage: Back to Fablewick link points at the library",
            back_link_href == "/fablewick/",
            f"href={back_link_href}",
        )

        page.close()
        browser.close()


def check_heritage_reader_page():
    """/heritage/read/:slug: the level control swaps page-1 text (Adults
    differs from Kids), the language control swaps it again (Gujarati),
    spread layout at 1440, stacked at 390, no console errors, no
    horizontal scroll at 390 - the same shape check_reader_page() runs
    for the Fablewick reader, against the Heritage reader's own level
    and 3-language controls instead.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()

        page = browser.new_page(viewport={"width": 1440, "height": 900})
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: console_errors.append(str(exc)))

        page.goto(BASE + f"heritage/read/{HERITAGE_READER_SLUG}", wait_until="networkidle", timeout=15000)
        page.wait_for_timeout(400)

        cover_loaded = page.evaluate(
            "() => { const img = document.querySelector('.reader-cover-img'); "
            "return !!img && img.complete && img.naturalWidth > 0; }"
        )
        check("heritage-reader: cover art loaded", cover_loaded)

        page.click(".reader-nav-next")
        page.wait_for_timeout(350)

        def page_text():
            return page.evaluate("document.querySelector('.reader-text')?.textContent ?? ''")

        kids_text = page_text()
        check("heritage-reader: page 1 has text under the default (Kids) level", len(kids_text) > 0, kids_text[:40])

        page.click(".heritage-level-control .heritage-level-btn:has-text('Adults')")
        page.wait_for_timeout(300)
        adults_text = page_text()
        check(
            "heritage-reader: Adults level changes page 1 text from Kids",
            adults_text != kids_text and len(adults_text) > 0,
            f"kids={kids_text[:40]!r} adults={adults_text[:40]!r}",
        )

        page.click(".reader-lang-btn")
        page.wait_for_timeout(150)
        page.click("button.reader-lang-option:has-text('Gujarati')")
        page.wait_for_timeout(300)
        gujarati_text = page_text()
        has_gujarati = page.evaluate(f"/[\\u0A80-\\u0AFF]/.test({json.dumps(gujarati_text)})")
        check(
            "heritage-reader: Gujarati language switch changes page text",
            has_gujarati and gujarati_text != adults_text,
            gujarati_text[:40],
        )

        tracks_desktop = grid_track_count(page, ".reader-book")
        check(
            "heritage-reader: spread layout (two columns) active at 1440",
            tracks_desktop == 2,
            f"tracks={tracks_desktop}",
        )

        page.screenshot(path=str(SHOTS / "heritage-reader-detail-spread-desktop.png"))

        check(
            "heritage-reader/desktop interaction: no console errors",
            len(console_errors) == 0,
            "; ".join(console_errors[:3]),
        )
        page.close()

        mobile = browser.new_page(viewport={"width": 390, "height": 844})
        mobile_errors = []
        mobile.on("console", lambda msg: mobile_errors.append(msg.text) if msg.type == "error" else None)
        mobile.on("pageerror", lambda exc: mobile_errors.append(str(exc)))

        mobile.goto(BASE + f"heritage/read/{HERITAGE_READER_SLUG}", wait_until="networkidle", timeout=15000)
        mobile.wait_for_timeout(400)
        mobile.click(".reader-nav-next")
        mobile.wait_for_timeout(350)

        tracks_mobile = grid_track_count(mobile, ".reader-book")
        check(
            "heritage-reader: stacked layout (one column) active at 390",
            tracks_mobile == 1,
            f"tracks={tracks_mobile}",
        )

        scroll_width = mobile.evaluate("document.documentElement.scrollWidth")
        check(
            "heritage-reader/mobile: no horizontal scroll at 390",
            scroll_width <= 391,
            f"scrollWidth={scroll_width}",
        )

        mobile.screenshot(path=str(SHOTS / "heritage-reader-detail-content-mobile.png"))

        check(
            "heritage-reader/mobile interaction: no console errors",
            len(mobile_errors) == 0,
            "; ".join(mobile_errors[:3]),
        )
        mobile.close()

        browser.close()


# ── wave 5: the shared header's per-route language chips ──────────────
def check_header_routes():
    """The header's language chips narrow by route (docs/v2-plan-2026-09-04.md
    wave-5 residual): all five on the library, only EN/HI/GU on the
    Heritage pages (its own edition only ever shipped three), and none on
    the Fablewick reader (which has its own in-stage language control -
    a second header row would just be a duplicate)."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        page.goto(BASE, wait_until="networkidle", timeout=15000)
        page.wait_for_timeout(300)
        library_chips = page.locator(".lang-chips .lang-chip").count()
        check("header: library shows 5 language chips", library_chips == 5, f"found {library_chips}")

        page.goto(BASE + "heritage", wait_until="networkidle", timeout=15000)
        page.wait_for_timeout(300)
        heritage_chips = page.eval_on_selector_all(".lang-chips .lang-chip", "els => els.map(e => e.textContent)")
        check(
            "header: /heritage shows exactly 3 language chips (EN, HI, GU)",
            len(heritage_chips) == 3,
            f"chips={heritage_chips}",
        )

        page.goto(BASE + f"heritage/read/{HERITAGE_READER_SLUG}", wait_until="networkidle", timeout=15000)
        page.wait_for_timeout(300)
        heritage_reader_chips = page.locator(".lang-chips .lang-chip").count()
        check(
            "header: /heritage/read/<slug> shows exactly 3 language chips",
            heritage_reader_chips == 3,
            f"found {heritage_reader_chips}",
        )

        page.goto(BASE + f"read/{READER_SLUG}", wait_until="networkidle", timeout=15000)
        page.wait_for_timeout(300)
        reader_chip_group = page.locator(".lang-chips").count()
        check(
            f"header: /read/{READER_SLUG} shows no header language chips (the reader has its own)",
            reader_chip_group == 0,
            f"found {reader_chip_group} .lang-chips group(s)",
        )

        page.close()
        browser.close()


# ── wave 8: one font, no italic, no free line ──────────────────────────
def check_manrope_font_samples():
    """Wave 8 (docs/v2-plan-2026-09-04.md): Mann - 'You have font that I
    don't like ... use font that I prefer.' Every text element's computed
    font-family should now START with Manrope. Sampled across the element
    kinds the plan names: body, h1, h2, a button, a card summary, a
    reader page paragraph, a Heritage level chip - one page load per
    route rather than one per selector.
    """
    samples = {
        "": {
            "body": "body",
            "h2 (section title)": ".section-title",
            "button (hero language chip)": ".hero-lang-chip",
            "card summary": ".book-card-summary",
        },
        "heritage": {
            "h1 (Heritage hero title)": ".heritage-hero-title",
            "Heritage level chip": ".heritage-level-btn",
        },
        f"read/{READER_SLUG}": {
            "reader page paragraph": ".reader-text p",
        },
    }

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        for route_path, selectors in samples.items():
            page.goto(BASE + route_path, wait_until="networkidle", timeout=15000)
            page.wait_for_timeout(400)
            if route_path.startswith("read/"):
                # the reader's first content page only carries text once
                # a page turn moves past the cover
                page.click(".reader-nav-next")
                page.wait_for_timeout(350)

            for label, selector in selectors.items():
                family = page.evaluate(
                    "(sel) => { const el = document.querySelector(sel); "
                    "return el ? getComputedStyle(el).fontFamily : null; }",
                    selector,
                )
                ok = bool(family) and family.strip().lstrip("'\"").startswith("Manrope")
                check(
                    f"font sample [{route_path or 'library'}] {label}: computed font-family starts with Manrope",
                    ok,
                    f"selector={selector} font-family={family}",
                )

        page.close()
        browser.close()


def main():
    build()
    httpd = serve()
    time.sleep(0.5)
    try:
        files = run_checks_and_shots()
        check_library_page()
        check_about_actions()
        check_reader_page()
        check_heritage_page()
        check_heritage_reader_page()
        check_header_routes()
        check_manrope_font_samples()
    finally:
        httpd.shutdown()

    print(f"\n{len(files)} screenshots written to {SHOTS}")

    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print(f"\n{passed}/{total} checks passed")

    if passed < total:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
