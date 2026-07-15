# Datapack → Wiki tools

Scripts that turn `datapacks.zip` into real wiki content. Re-run these any
time the server's datapacks change instead of hand-editing the pages they
own.

## Setup
No dependencies beyond Python 3 (uses only the standard library).

## Workflow
```
# 1. Unzip your datapacks somewhere
unzip datapacks.zip -d ~/datapacks

# 2. Extract structured data from them
python3 tools/extract_data.py ~/datapacks

# 3. Rebuild the site
python3 tools/build_all.py
```
`build_all.py` runs `build_static_pages.py` (every template/placeholder
page — keeps every sidebar in sync with `site_common.py`'s NAV) and then
`build_dynamic_pages.py` (overlays the data-driven pages below with real
data, and finishes by rebuilding the search index from the final HTML) in
the right order. Run it whenever you touch `site_common.py`'s NAV, even if
you haven't re-extracted new data.

## What gets extracted, and where it goes

| Source in datapacks | Extracted to | Rendered page |
|---|---|---|
| `cobblemonraiddens/raid/boss/*.json` + `boss_additions/*.json` | `tools/data/raids.json` | `gameplay/mechanics/raids.html` |
| `*/data/cobbleverse/worldgen/structure/**/*.json` (all 4 region packs — gyms, leagues, monuments, landmarks) + matching `structure_set/` | `tools/data/structures.json` | `gameplay/world/structures.html` + `gameplay/world/legendary-monuments.html` |
| *(derived from `pokemon.json`'s spawn conditions — no separate source file)* | — | `gameplay/world/biomes.html` |
| *(reference content, not datapack-sourced — see note below)* | — | `gameplay/world/blocks.html` |
| `*/tmcraft/recipe/*.json` | `tools/data/tm_recipes.json` | `gameplay/items/tms.html` |
| `*/cobblemon/fossils/*.json` | `tools/data/fossils.json` | `gameplay/items/fossils.html` |
| `*/lumymon/trades/*_cartographer.json` | `tools/data/lumymon_maps.json` | `gameplay/server-features/lumymon.html` |
| `*/cobblemon/spawn_pool_world/*.json` (all 1024 species) | `tools/data/pokemon.json` → trimmed copy at `assets/data/pokemon.json` | `gameplay/pokemon/index.html` (Pokédex app — see below) |
| `*/cobblemon/species/**/*.json` (10 pack-tuned legendaries) | `tools/data/species_overrides.json` | not yet rendered — full stat blocks for Zapdos/Rayquaza/Lugia/etc. if you want to hand-write callouts for the ones this pack rebalances |
| `COBBLEVERSE-RCT-DP-v19/data/rctmod/trainers/*.json` (155 trainers) + matching `mobs/trainers/single/*.json` for spawn biome | `tools/data/trainers.json` | `gameplay/trainers/*.html` (Trainers & Gyms — one page per region + villains + other) |
| `*/zamegas/recipe/*.json` + `*/mega_showdown/recipe/*.json` | `tools/data/mega_evolutions.json` | `gameplay/items/mega-evolution.html` |
| *(none — built from the other pages' final rendered HTML, plus `pokemon.json`/`trainers.json`)* | `assets/data/search-index.json` | powers the search box in the sidebar on every page |

Every extracted page opens with a callout marking it as auto-generated, and
still has `fill`-style placeholders for the parts no datapack can answer
(where to find something in-world, tips, strategy) — the goal is to remove
the tedious data-entry, not replace the writing.

### The Item Database (`gameplay/items/database.html`)
Scraped from the official Cobblemon Wiki's `Category:Item` (223 pages) and
its curated `Items` overview page (which supplies clean categories: Poké
Ball, Held Item, Evolution Items, Medicine, Stat-Changing, Berries &
Agriculture, Food & Consumables, Archaeology, Miscellaneous). 193 items made
it through after filtering out non-item wiki pages (talk/template/user
sandbox pages that were incorrectly in the category). Summaries are written
fresh for this wiki, not copied from the source — each card links out to the
official page for full detail/images. Source data: `tools/data/items.json`
(re-run the scrape and re-paste into `tools/data/items.json` if the item
roster changes — there's no automated re-scrape script since it required a
one-time upload of the category page's HTML).

### Advanced Search (`search.html`)
A dedicated results page with type + section filters, reading the same
`assets/data/search-index.json` the sidebar search uses. The sidebar
dropdown's "See all results & filters" link lands here with the query
pre-filled. No separate data file — `build_search_page()` in
`build_static_pages.py` just builds the shell; `assets/js/advsearch.js`
does the filtering client-side.

### The Blocks page (`gameplay/world/blocks.html`)
Unlike everything else in this table, block definitions (what a Healing
Machine does, what an Apricorn Tree drops) are compiled into the Cobblemon
mod jar itself — they're not datapack-configurable, so there's nothing for
`extract_data.py` to read. This page is hand-written reference content
sourced from the official Cobblemon Wiki instead, and won't auto-update —
edit `build_blocks_page()` in `build_static_pages.py` directly if a future
Cobblemon version changes something.

### The Pokédex app (`gameplay/pokemon/index.html`)
This one works differently from the other 7 pages. The datapacks only give us
*this server's* spawn data (biome, rarity, level range, time/weather) — they
don't include base types/abilities/stats, since those live inside the
Cobblemon mod jar itself, not in a datapack. Rather than hand-type or guess
that data for 1024 species, `assets/js/pokedex.js` fetches it live from the
public PokeAPI in the browser, in small background batches, and caches the
result in `localStorage` (`cobbleverse_pokedex_cache_v1`) so repeat visits
are instant and the page never goes stale when Cobblemon updates. Sprite art
loads immediately from PokeAPI's static sprite CDN by dex number — no API
call needed for images. If you're hosting somewhere that blocks outbound
fetches to `pokeapi.co` for visitors, the grid/search/spawn-data still work;
only the live type/ability/stat panel won't populate.

## Extending this
Found in the datapacks but not extracted yet — good next targets if you
want to add another extractor function to `extract_data.py`:
- `lumymon/recipe/*_radar.json` — craftable legendary radar items (~30 files)
- `COBBLEVERSE-Loot-DP-v11` loot tables — item drop tables per structure/mob
- `rctmod/dialogs/trainers/**` — trainer battle-start/win/lose flavor lines
  (translation *keys* only live in the datapack; the actual English text is
  baked into the mod's lang file, not shipped here, so this needs the lang
  file pulled from the mod jar to be worth extracting)

Each follows the same pattern: write an `extract_x()` function in
`extract_data.py` that returns a list/dict, add it to the `datasets` dict in
`main()`, then add a `build_x_page()` function to `build_dynamic_pages.py`
that reads the JSON and calls `write_page(...)`.

## Files
- `site_common.py` — the NAV model and HTML template every page shares. Add
  new pages to `NAV` here first. Also holds `POKEMON_NAME_FIXES` — the small
  list of species whose slug doesn't title-case cleanly (Mr. Mime, Porygon-Z,
  Farfetch'd, etc.) — add to it if a new one shows up oddly rendered.
- `extract_data.py` — datapacks → JSON.
- `build_static_pages.py` — regenerates every template page (safe to run
  any time; doesn't touch the 8 data-driven pages listed above).
- `build_dynamic_pages.py` — regenerates the data-driven pages from
  `tools/data/*.json`. Falls back to a blank template per page if that
  page's JSON is missing.
- `build_all.py` — runs the two build scripts in order.
- `data/` — extracted JSON cache (safe to delete and regenerate).
