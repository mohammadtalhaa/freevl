# Free Voice Labs — Next.js (App Router)

A complete Next.js conversion of the static Free Voice Labs site, ready to
deploy on Vercel. No page was dropped.

## Routes (all 13 pages)

| Route | Source page |
|---|---|
| `/` | `index.html` |
| `/about` | `about.html` |
| `/ai-voices` | `ai-voices.html` |
| `/premium-voices` | `premium-voices.html` |
| `/realistic-voices` | `realistic-voices.html` |
| `/faqs` | `faqs.html` |
| `/contact` | `contact.html` |
| `/feature-requests` | `feature-requests.html` |
| `/privacy` | `privacy.html` |
| `/terms` | `terms.html` |
| `/disclaimers` | `disclaimers.html` |
| `/sitemap` | `sitemap.html` (the visual sitemap page) |
| `/admin` | `admin.html` |

Old `.html` URLs still work: `next.config.mjs` permanently redirects
`/about.html` → `/about`, `/index.html` → `/`, and so on for every page,
so bookmarks, ads and search results do not break.

`public/` holds the static assets: `logo.png`, `favicon.ico`,
`og-image.png`, `apple-touch-icon.png`, `shared.css`, `robots.txt`,
`public/sitemap.xml` (now listing the clean routes) and `ads.txt`.
`/sitemap.xml` and `/robots.txt` are served from `public/` by Next.js.

## The v6 badge is gone

Every page used to show a small `v6` badge next to "Free Voice Labs" in
the header (`<span class="island-brand-badge">v6</span>`). That span and
its CSS rules were removed from all 13 pages. A search of the built
project for `v6` returns nothing.

## How the conversion is built — read this before editing

This is a faithful migration, not a hand rewrite of every component into
idiomatic React, and it says so plainly so you are not misled:

- `scripts/extract-legacy.py` splits each original HTML page into
  `lib/legacy/<slug>.json`: title/description/Open Graph/canonical,
  JSON-LD, the page's CSS, its body HTML, and its scripts.
- `app/<route>/page.jsx` is a Next.js server component: it exports real
  Next.js `metadata` (title, description, canonical, Open Graph, Twitter)
  and renders the page's JSON-LD.
- `components/LegacyPage.jsx` is a client component: it renders the page
  CSS and body HTML server-side (so the content is in the served HTML),
  then injects the page's original scripts once after mount, in their
  original order. Injected classic scripts run in global scope exactly as
  the original `<script>` tags did, and they expose their handlers on
  `window`, so the TTS studio, blends, podcast mode, voice cloning UI,
  auth modals, feedback, and checkout keep working as before.
- Navigation is a full page load (the original `<a>` links), not Next.js
  client-side navigation, because the legacy scripts boot once per page
  load. That is intentional.
- Internal links were rewritten from `.html` to clean routes, and
  `logo.png` to `/logo.png`, so they resolve under clean routes.
  Plain text (for example the file tree on the visual sitemap page) was
  not rewritten.

A full idiomatic React rewrite — one component at a time, starting with
the homepage studio — is still possible later, page by page, and this
project is the correct base for it. It is not claimed here.

## What was NOT changed

- The backend. Pages still call the Hugging Face backend
  (`mohammadtalhaa-free-voice-labs-backend.hf.space`) directly. No API
  routes were added and no backend code is in this repo.
- Pricing and checkout behaviour. The homepage kept here is the uploaded
  `index.html` (Weekly $1.99 / Monthly $5.99, old `/api/checkout` flow).
  The duplicate homepages `index__1.html` and `index__3.html` were NOT
  converted — they are duplicate homepages, and `index__3.html` is a
  different ($4.99 Safepay) version that needs the patched backend. If you
  want that homepage live, swap `lib/legacy/home.json` by re-running the
  extractor against that file, together with the backend redeploy.
- `admin.html` is still only client-side gated. Moving to Next.js does
  not add real admin authentication; it is set `noindex` and disallowed
  in `robots.txt`, as before.

## Run it

```bash
npm install
npm run dev        # http://localhost:3000
npm run build
npm start
```

Node 18.18+ is required by Next.js 15; Node 20+ is recommended.

## Deploy on Vercel

1. Push this folder to a Git repo (or use `vercel` CLI from this folder).
2. Import it in Vercel. Framework Preset: **Next.js**. Leave the build
   command (`next build`) and output directory at their defaults.
3. Add the domains `freevoicelabs.com` and `www.freevoicelabs.com` in
   Vercel → Project → Settings → Domains, and point DNS as Vercel shows.
   `www` redirects to the apex in `next.config.mjs`; the apex is
   canonical, matching `sitemap.xml`.
4. Test on the preview URL first: every route above, voice generation,
   sign-in, and checkout. The backend is unchanged, so a failure there
   is not caused by this conversion.

## Re-extracting after an HTML edit

If you edit the original static HTML, re-run:

```bash
python3 scripts/extract-legacy.py
```

That regenerates `lib/legacy/*.json` from `~/workspace/user/files/*.html`
(the extractor's `SRC` path — adjust it if your source files live
elsewhere). Then rebuild.
