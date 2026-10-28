#!/usr/bin/env python3
"""Extract the uploaded static Free Voice Labs pages into Next.js legacy data.

What this does, and what it does NOT do:
- Splits each original HTML page into: metadata, JSON-LD, page CSS,
  body HTML, and the page's original inline/external scripts.
- Removes the visible "v6" badge:
    <span class="island-brand-badge">v6</span>
  and the now-orphaned .island-brand-badge CSS rules.
- Rewrites internal links from legacy .html URLs to clean Next.js routes
  (href="/about.html" -> href="/about", href="index.html" -> href="/",
  JS "/admin.html" -> "/admin") and logo.png -> /logo.png, so assets and
  links resolve under clean routes. Plain text (e.g. the file tree on the
  visual sitemap page) is NOT rewritten.
- Does NOT rewrite the pages' JavaScript into React. The original scripts
  are preserved verbatim (except the link rewrites above) and are injected
  by components/LegacyPage.jsx after the page HTML mounts, so the TTS
  studio, auth, blends, podcast, feedback and checkout behaviour is the
  same as the static site. A full idiomatic React rewrite is a separate,
  page-by-page project — see README.md.

Run from the project root:  python3 scripts/extract-legacy.py
Input:  ../user/files/*.html  (the uploaded static site)
Output: lib/legacy/<slug>.json
"""
import html as html_lib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path.home() / "workspace" / "user" / "files"
OUT = ROOT / "lib" / "legacy"

# filename -> (slug used for the JSON file, Next.js route)
PAGES = {
    "index.html": ("home", "/"),
    "about.html": ("about", "/about"),
    "ai-voices.html": ("ai-voices", "/ai-voices"),
    "premium-voices.html": ("premium-voices", "/premium-voices"),
    "realistic-voices.html": ("realistic-voices", "/realistic-voices"),
    "faqs.html": ("faqs", "/faqs"),
    "contact.html": ("contact", "/contact"),
    "feature-requests.html": ("feature-requests", "/feature-requests"),
    "privacy.html": ("privacy", "/privacy"),
    "terms.html": ("terms", "/terms"),
    "disclaimers.html": ("disclaimers", "/disclaimers"),
    "sitemap.html": ("sitemap", "/sitemap"),
    "admin.html": ("admin", "/admin"),
}
# legacy .html filename -> clean route, for href / JS rewrites
ROUTE_BY_FILE = {name: route for name, (_slug, route) in PAGES.items()}
ROUTE_BY_FILE["index.html"] = "/"


def clean_route_for_href(value: str) -> str:
    """Map a legacy href value to a clean route, or return it unchanged."""
    if value.startswith("https://freevoicelabs.com/"):
        rest = value[len("https://freevoicelabs.com/"):]
        if rest in ROUTE_BY_FILE:
            return "https://freevoicelabs.com" + ROUTE_BY_FILE[rest]
        return value
    if value.startswith("/"):
        rest = value[1:]
        if rest in ROUTE_BY_FILE:
            return ROUTE_BY_FILE[rest]
        return value
    if value in ROUTE_BY_FILE:
        return ROUTE_BY_FILE[value]
    return value


def rewrite_hrefs(fragment: str) -> str:
    def repl(m):
        return 'href="' + clean_route_for_href(m.group(1)) + '"'
    return re.sub(r'href="([^"]+)"', repl, fragment)


def rewrite_js_routes(code: str) -> str:
    for fname, route in ROUTE_BY_FILE.items():
        code = code.replace('"/' + fname + '"', '"' + route + '"')
        code = code.replace("'/" + fname + "'", "'" + route + "'")
    return code


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for filename, (slug, route) in PAGES.items():
        src = SRC / filename
        if not src.exists():
            print(f"SKIP missing {src}", file=sys.stderr)
            continue
        text = src.read_text(errors="ignore")

        # --- Remove the v6 badge (visible) and its CSS rules (orphaned) ---
        text = text.replace('<span class="island-brand-badge">v6</span>', "")
        text = re.sub(r"\.island-brand-badge\s*\{[^}]*\}", "", text)
        assert "v6" not in text, f"v6 still present in {filename}"

        head = text[text.find("<head>"):text.find("</head>")]
        body_match = re.search(r"<body([^>]*)>(.*)</body>", text, re.S)
        assert body_match, f"no body in {filename}"
        body_attrs, body_html = body_match.group(1), body_match.group(2)
        body_id = None
        m_id = re.search(r'id="([^"]+)"', body_attrs)
        if m_id:
            body_id = m_id.group(1)

        # --- Metadata from head ---
        def meta(name=None, prop=None):
            if name:
                m = re.search(r'<meta name="' + re.escape(name) + r'" content="([^"]*)"', head)
            else:
                m = re.search(r'<meta property="' + re.escape(prop) + r'" content="([^"]*)"', head)
            return html_lib.unescape(m.group(1)) if m else None

        title_m = re.search(r"<title>(.*?)</title>", head, re.S)
        title = html_lib.unescape(title_m.group(1).strip()) if title_m else "Free Voice Labs"
        description = meta(name="description")
        robots = meta(name="robots")
        og_title = meta(prop="og:title")
        og_desc = meta(prop="og:description")
        og_image = meta(prop="og:image")
        og_url = meta(prop="og:url")

        json_ld = []
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', head, re.S):
            raw = m.group(1).strip()
            json.loads(raw)  # validate
            json_ld.append(raw)

        # --- CSS ---
        css = "\n".join(m.group(1) for m in re.finditer(r"<style[^>]*>(.*?)</style>", head, re.S))

        # --- Scripts: head externals first, then body scripts, in order ---
        scripts = []
        for m in re.finditer(r"<script([^>]*)>(.*?)</script>", head, re.S):
            attrs, content = m.group(1), m.group(2)
            if "ld+json" in attrs:
                continue
            src_m = re.search(r'src="([^"]+)"', attrs)
            if src_m:
                scripts.append({"src": src_m.group(1), "async": "async" in attrs})
        for m in re.finditer(r"<script([^>]*)>(.*?)</script>", body_html, re.S):
            attrs, content = m.group(1), m.group(2)
            src_m = re.search(r'src="([^"]+)"', attrs)
            if src_m:
                scripts.append({"src": src_m.group(1), "async": "async" in attrs})
            else:
                scripts.append({"content": rewrite_js_routes(content)})

        # --- Body HTML: strip scripts, rewrite links/assets ---
        body_html = re.sub(r"<script[^>]*>.*?</script>", "", body_html, flags=re.S)
        body_html = rewrite_hrefs(body_html)
        body_html = body_html.replace('src="logo.png"', 'src="/logo.png"')

        data = {
            "slug": slug,
            "route": route,
            "title": title,
            "description": description,
            "robots": robots,
            "ogTitle": og_title,
            "ogDescription": og_desc,
            "ogImage": og_image,
            "ogUrl": ("https://freevoicelabs.com" + route) if route != "/" else "https://freevoicelabs.com/",
            "jsonLd": json_ld,
            "css": css,
            "bodyId": body_id,
            "bodyHtml": body_html.strip(),
            "scripts": scripts,
        }
        (OUT / f"{slug}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1))
        print(f"{filename:25} -> {slug}.json  title={title[:60]!r} css={len(css)} body={len(body_html)} scripts={len(scripts)} jsonld={len(json_ld)}")


if __name__ == "__main__":
    main()
