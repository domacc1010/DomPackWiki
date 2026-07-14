# How to edit this wiki (without the generators fighting you)

There are three layers. Pick the right one and your edits are permanent.

## 1. `content/` — hand-written pages (your main tool)
Put HTML at `content/<page-path>` and it **is** that page's body forever.
Rebuilds keep the sidebar fresh around it but never touch your HTML.

- Start from what a generated page already has:
  `python3 tools/eject.py gameplay/items/tms.html`
- Go fully manual on every template page at once:
  `python3 tools/eject.py --all-static`
- Undo: delete the file from `content/`.
- Already hand-written this way: **Items → Crafting** (Poké Ball recipes,
  apricorns, specialty balls — cross-checked against the official
  Cobblemon Wiki).

## 2. `assets/data/pokemon-custom.json` — custom Pokémon cards
Add anything to any Pokémon's Pokédex card: notes, extra sections (any
HTML), your own image, a name override, or hide the auto stats/spawn blocks.
**Edits show on refresh — no rebuild at all.** Zapdos has a live example
entry. Full field docs: `assets/data/README.md`.

## 3. Generated pages — data that's silly to hand-type
Pokédex spawn data (1024 species), trainer teams (155), TM recipes (483),
raids, structures. These regenerate from the server's datapacks via
`tools/build_all.py`. If you want manual control of one anyway → eject it
(layer 1). The only page that can't be ejected is the Pokédex app itself —
that's what layer 2 is for.

## Rules of thumb
- Editing a page's text/layout → `content/` (eject first if it has
  generated data worth keeping).
- Adding info to a Pokémon's card → `pokemon-custom.json`.
- Datapacks changed on the server → re-run
  `python3 tools/extract_data.py <datapacks>` then `python3 tools/build_all.py`.
  Your `content/` files and `pokemon-custom.json` are untouched by both.
- Never hand-edit the built `.html` files at the site root — those are
  build output and will be overwritten. Edit in `content/` instead.
