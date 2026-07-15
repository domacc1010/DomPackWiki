# CobbleVerse Wiki — starter site

Static HTML/CSS site, no build step. Unzip and open `index.html` directly in
a browser, or drag the folder onto Netlify / GitHub Pages / any static host.

## What's here
- **EDITING.md** — read this first: how to hand-edit any page (content/ overrides + tools/eject.py) or any Pokémon card (assets/data/pokemon-custom.json) without rebuilds ever overwriting your work.
- 60+ pages, all cross-linked through a real sidebar nav (collapsible sections).
- One shared stylesheet: `assets/style.css`.
- **Pokémon** (`gameplay/pokemon/index.html`) is a searchable/filterable
  Pokédex app covering all 1024 spawnable species — sprite art, live
  types/abilities/base stats from PokeAPI, and this server's own spawn data
  (biome, rarity, level range, time/weather) pulled from the datapacks. Fully
  auto-generated — see `tools/README.md`.
- **Trainers & Gyms** (`gameplay/trainers/`) covers all 155 named trainers —
  Gym Leaders, Elite Four, Champions, rivals, and full villainous-team
  rosters (Team Rocket, Team Galactic, Team Aqua, Team Magma) — with real
  teams (species, level, moves, nature, ability, items) pulled straight from
  the roaming-trainer datapack.
- **Search** (top of the sidebar, every page) finds anything on the site —
  page content, all 1024 Pokémon, every named trainer, and every item — from
  a single box, live as you type. Built from `assets/data/search-index.json`,
  regenerated automatically by `tools/build_dynamic_pages.py` as its last
  step (it scans the final rendered HTML of every page, so it always
  reflects current content).
- **Item Database** (`gameplay/items/database.html`) — 193 items scraped from
  the official Cobblemon Wiki's item category, organized into the wiki's own
  categories (Poké Ball, Held Item, Evolution Items, Medicine, etc.) with
  original one-line summaries and a link to the official page for full
  detail. Same search/filter grid pattern as the Pokédex.
- **Advanced Search** (`search.html`, linked at the top of every sidebar) —
  a full results page searching everything at once (pages, Pokémon,
  trainers, items) with type and category filters. The sidebar's quick
  search links here via "See all results & filters."
- Items section is an index page with a copyable in-page template, since it
  will have more entries than the rest of the site — duplicate the template
  block into a new page per item once you're ready.

## Images
Drop screenshots/renders into `assets/images/` and reference them with the
`.img-frame` wrapper for a themed border + caption:
```html
<figure class="img-frame">
  <img src="../../assets/images/your-file.png" alt="Description">
  <figcaption>Caption text</figcaption>
</figure>
```
Use `.gallery-grid` around multiple `.img-frame` elements for a grid layout.

### Hover previews (image peek)
Any text can show a floating image preview on hover — hover the preview to
enlarge it, click to open full-size:
```html
<span class="img-peek" data-img-base="../../assets/images/LenMonu/sky_pillar">Sky Pillar</span>
```
`data-img-base` is the image path **without extension** (.png/.jpg/.jpeg/.webp
all work). If no image exists yet, hovering just shows nothing — so markup can
go in before the screenshot is taken, and the image appears the moment the
file is dropped in, no rebuild needed. The Legendary Monuments page already
has this on every site name, reading from `assets/images/LenMonu/` — see the
README in that folder for the exact expected filenames. In build scripts, use
the `img_peek()` helper from `tools/site_common.py`.

## To add a new page
1. Copy the closest existing page as a starting point (matching folder depth).
2. Update the `<title>`, `<h1>`, and content.
3. Add a link to it in the sidebar `<nav>` — that block is identical across
   every page, so search-and-replace across all files if adding a nav item,
   or just add it manually as you go.

## Hosting
Any static host works (GitHub Pages, Netlify, Cloudflare Pages, Vercel, or
just a folder on your own web server). No server-side code, no database.
