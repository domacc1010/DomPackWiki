# Pokémon

`index.html` is now **auto-generated** — don't hand-edit it, it gets
overwritten every time `tools/build_dynamic_pages.py` runs. It's a
Cobbledex-style searchable/filterable Pokédex covering all 1024 spawnable
species: search by name/dex number, filter by type/generation/rarity, click
a card for full detail (types, abilities, base stats, and this server's own
spawn conditions — biome, rarity, level range, time/weather). See
`tools/README.md` for how the data pipeline works.

## Optional: deep-dive pages for standout Pokémon
The Pokédex app covers base data for everything automatically. If you want
to hand-write a richer page for a specific Pokémon — a signature raid boss,
a gym ace, a community favorite — use `_TEMPLATE.md` as a starting point for
the parts no datapack can answer (drops, breeding notes, competitive builds,
trivia, screenshots) and link it from the relevant card or from here.

## Workflow for a deep-dive page
1. Copy `_TEMPLATE.md` to `{pokemon-name}.md`.
2. Skip re-typing types/abilities/evolution/spawn — the Pokédex app already
   has that, sourced live + from the datapacks.
3. Cross-check competitive info (natures, EV spreads, movesets) against
   Pokémon Showdown.
4. Add server-specific notes only you would know (observed drop rates,
   where it actually feels common on *this* server's world, etc.).

## Status Tracker
Use this table to track progress on hand-written deep-dive pages only —
everything else is covered by the Pokédex app.

| Pokémon | Page Created | Data Verified | Screenshots | Notes |
|---|---|---|---|---|
| | | | | |
