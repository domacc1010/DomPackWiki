# CobbleVerse Wiki — starter site

Static HTML/CSS site, no build step. Unzip and open `index.html` directly in
a browser, or drag the folder onto Netlify / GitHub Pages / any static host.

## What's here
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
  page content, all 1024 Pokémon, and every named trainer — from a single
  box. Built from `assets/data/search-index.json`, regenerated automatically
  by `tools/build_dynamic_pages.py` as its last step (it scans the final
  rendered HTML of every page, so it always reflects current content).
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

## To add a new page
1. Copy the closest existing page as a starting point (matching folder depth).
2. Update the `<title>`, `<h1>`, and content.
3. Add a link to it in the sidebar `<nav>` — that block is identical across
   every page, so search-and-replace across all files if adding a nav item,
   or just add it manually as you go.

## Hosting
Any static host works (GitHub Pages, Netlify, Cloudflare Pages, Vercel, or
just a folder on your own web server). No server-side code, no database.
