"""
Site mirror template — fill in the variables below before running.
"""
import os
import time
import urllib.parse
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ── Configure these ──────────────────────────────────────────────────────────
TARGET_URL    = "https://example.com/some/page"
OUTPUT_DIR    = Path("mirrored-site")
BASE_DOMAIN   = urllib.parse.urlparse(TARGET_URL).netloc  # auto-derived

# Path prefixes to skip entirely (e.g. blogs, news, tags)
EXCLUDED_PATHS = ["/blog", "/blogs", "/news", "/tag", "/tags"]

# Only follow links whose path starts with this prefix (set to None for all)
SECTION_FILTER = None  # e.g. "/architecture/"

# How many link levels deep to crawl (0 = only the target page)
MAX_DEPTH = 2

# Polite delay between requests (seconds)
REQUEST_DELAY = 0.3
# ─────────────────────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

session = requests.Session()
session.headers.update(HEADERS)

visited: set[str] = set()
downloaded_assets: set[str] = set()
page_count = 0
error_count = 0


def is_excluded(url: str) -> bool:
    path = urllib.parse.urlparse(url).path.lower()
    return any(path.startswith(ex) for ex in EXCLUDED_PATHS)


def in_section(url: str) -> bool:
    if SECTION_FILTER is None:
        return True
    return urllib.parse.urlparse(url).path.startswith(SECTION_FILTER)


def url_to_local_path(url: str, base_dir: Path) -> Path:
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.lstrip("/")
    if not path or path.endswith("/"):
        path = path + "index.html"
    elif "." not in Path(path).name:
        path = path + "/index.html"
    return base_dir / parsed.netloc / path


def save_file(path: Path, content) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")
    print(f"  Saved: {path}")


def download_asset(url: str) -> None:
    if url in downloaded_assets:
        return
    downloaded_assets.add(url)
    try:
        r = session.get(url, timeout=20)
        r.raise_for_status()
        save_file(url_to_local_path(url, OUTPUT_DIR), r.content)
        time.sleep(REQUEST_DELAY)
    except Exception as e:
        global error_count
        error_count += 1
        print(f"  Asset error {url}: {e}")


def mirror_page(url: str, depth: int = 0) -> None:
    global page_count, error_count

    if url in visited or depth > MAX_DEPTH:
        return
    if is_excluded(url):
        print(f"  Skipping (excluded): {url}")
        return

    parsed = urllib.parse.urlparse(url)
    if parsed.netloc and parsed.netloc != BASE_DOMAIN:
        return  # external domain — skip

    visited.add(url)
    print(f"\n[depth={depth}] Mirroring: {url}")

    try:
        r = session.get(url, timeout=30)
        r.raise_for_status()
    except Exception as e:
        error_count += 1
        print(f"  Fetch error: {e}")
        return

    soup = BeautifulSoup(r.text, "lxml")

    # Download linked assets (CSS, images, JS)
    for tag, attr in [("img", "src"), ("link", "href"), ("script", "src")]:
        for el in soup.find_all(tag):
            src = el.get(attr)
            if not src:
                continue
            abs_url = urllib.parse.urljoin(url, src)
            p = urllib.parse.urlparse(abs_url)
            if p.scheme in ("http", "https") and p.netloc == BASE_DOMAIN:
                if not is_excluded(abs_url):
                    download_asset(abs_url)

    save_file(url_to_local_path(url, OUTPUT_DIR), r.text)
    page_count += 1

    if depth < MAX_DEPTH:
        for a in soup.find_all("a", href=True):
            href = urllib.parse.urljoin(url, a["href"])
            p = urllib.parse.urlparse(href)
            if p.netloc != BASE_DOMAIN:
                continue
            if not is_excluded(href) and in_section(href):
                mirror_page(href, depth + 1)
            time.sleep(REQUEST_DELAY)


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Starting mirror of: {TARGET_URL}")
    print(f"Output directory  : {OUTPUT_DIR.resolve()}")
    print(f"Max depth         : {MAX_DEPTH}")
    print(f"Excluded paths    : {EXCLUDED_PATHS}")
    print(f"Section filter    : {SECTION_FILTER or 'none (all same-domain links)'}\n")

    mirror_page(TARGET_URL)

    print(f"\nDone.")
    print(f"  Pages mirrored : {page_count}")
    print(f"  Assets saved   : {len(downloaded_assets)}")
    print(f"  Errors         : {error_count}")
    print(f"  Output folder  : {OUTPUT_DIR.resolve()}")
