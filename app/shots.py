"""
Builds dist/, serves it on 127.0.0.1:8794, and screenshots each route at
1440x900 and 390x844 into _shots/. Modelled on mann-landing-v3's shots.py
(claude-workspace/1-Projects/mann-landing-v3/shots.py). Run after
`npm run build` so it screenshots the real production bundle.

Requires: pip install playwright && playwright install chromium.
"""
import http.server
import socketserver
import subprocess
import sys
import threading
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
SHOTS = ROOT / "_shots"
PORT = 8794
BASE = f"http://127.0.0.1:{PORT}/fablewick/"
VIEWPORTS = {"desktop": (1440, 900), "mobile": (390, 844)}

# path -> screenshot-file slug. dist/ is served at /fablewick/ so the
# base-path routing (vite.config.ts base: '/fablewick/') matches how
# GitHub Pages actually serves it.
ROUTES = {
    "library": "",
    "reader": "read/pip-and-the-lost-cloud",
    "heritage": "heritage",
    "heritage-reader": "heritage/read/dry-banyan-twig",
}


def build():
    subprocess.run(["npm", "run", "build"], cwd=ROOT, check=True, shell=True)


def serve():
    # Serves dist/ at /fablewick/ (matching vite.config.ts's base and how
    # GitHub Pages serves it), with an SPA fallback to index.html for any
    # path that isn't a real file so a direct navigation to a client
    # route (/read/:slug etc.) renders the app instead of 404ing.
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


def settle_reveals(page, viewport_height):
    # Reveal (a fade-up on IntersectionObserver) never fires for anything
    # below the fold unless the page is actually scrolled - a full-page
    # screenshot only stitches whatever has already rendered, it doesn't
    # scroll anything into view on its own. Walk down the document a
    # viewport-height at a time (half a viewport of overlap) so every
    # Reveal passes through the viewport at least once before the shot
    # below - a fixed step count misses content on the much taller mobile
    # stack, whose full height is several viewports.
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


def shoot():
    SHOTS.mkdir(exist_ok=True)
    files = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, (width, height) in VIEWPORTS.items():
            for route_name, route_path in ROUTES.items():
                page = browser.new_page(viewport={"width": width, "height": height})
                page.goto(BASE + route_path, wait_until="networkidle")
                page.wait_for_timeout(400)  # let webfonts settle
                settle_reveals(page, height)
                path = SHOTS / f"{route_name}-{name}.png"
                page.screenshot(path=str(path), full_page=True)
                files.append(path)
                page.close()
        browser.close()
    return files


def main():
    build()
    httpd = serve()
    time.sleep(0.5)
    try:
        files = shoot()
    finally:
        httpd.shutdown()

    print(f"{len(files)} screenshots written to {SHOTS}")
    for f in files:
        print(f)


if __name__ == "__main__":
    sys.exit(main())
