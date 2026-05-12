---
name: site-mirror
description: Mirrors/clones websites locally by downloading HTML, CSS, JS, and images. Use this skill whenever the user shares a URL and wants to: download a site, clone a site, mirror a page, scrape a website offline, save a site locally, copy a webpage, or archive a URL. Trigger even if the user says things like "baixa esse site", "salva essa página", "clona esse link", "quero esse site offline" or similar. Always use this skill when the user provides a URL and wants it saved locally.
---

# Site Mirror Skill

Mirror any website to a local folder — all HTML, CSS, JS, and images downloaded automatically.

## Step 1 — Install dependencies

Before doing anything else, ensure the required Python packages are installed:

```bash
pip install requests beautifulsoup4 lxml
```

If pip isn't available, try `pip3`. If Python isn't installed, tell the user to install Python from python.org first.

## Step 2 — Ask the user these questions (all at once, in one message)

Ask concisely:

1. **Output folder name** — where to save the files (default: a slug based on the URL, e.g. `amsterdam-architecture`)
2. **Crawl depth** — how many link levels to follow from the starting page (default: 2; use 0 for just the single page)
3. **Paths to exclude** — URL path prefixes to skip, like `/blog`, `/news`, `/shop` (default: `/blog`, `/blogs`, `/news`, `/tag`, `/tags`)
4. **Follow only same-section links?** — e.g. if the URL is `/architecture/X`, only follow links under `/architecture/` (default: yes)

If the user seems like a beginner or in a hurry, suggest the defaults and ask them to confirm with a simple "ok" or specify what they want changed.

## Step 3 — Generate and run the mirror script

Use the bundled template at `scripts/mirror_site.py` (next to this SKILL.md) as your base. Fill in the user's choices and write the final script to the working directory as `mirror_<slug>.py`, then run it.

Key parameters to fill in:
- `TARGET_URL` — the URL the user provided
- `OUTPUT_DIR` — the folder name from Step 2
- `EXCLUDED_PATHS` — list of path prefixes to skip
- `max_depth` — crawl depth from Step 2
- `SECTION_FILTER` — the path prefix to restrict link-following to (e.g. `/architecture/`), or `None` to follow all same-domain links

## Step 4 — Report results

After the script finishes, tell the user:
- Where the files were saved (absolute path)
- How many pages were mirrored
- Any errors or skipped URLs
- How to open the site: open `<output_dir>/<domain>/index.html` in a browser

## Edge cases

- **Site blocks scrapers**: Add a realistic User-Agent (already in the template). If still blocked, mention that the site may require a browser-based tool.
- **JavaScript-heavy sites**: The script downloads HTML as-is. If the page needs JS to render content, warn the user and suggest tools like `playwright` or `selenium` for a full render.
- **Large sites**: If depth > 2 or there are thousands of links, warn the user it may take a long time and suggest increasing the delay between requests.
- **HTTPS errors**: The template handles HTTPS natively via `requests`. No extra packages needed.
