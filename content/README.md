# content/ — your hand-written pages

Any file here **replaces the generated body** of the page at the same path.
`content/gameplay/items/crafting.html` = the body of
`gameplay/items/crafting.html`. The build still wraps it in the shared
sidebar/template (so navigation never drifts), but the body itself is yours —
**no rebuild will ever overwrite it.**

- Take over an existing generated page, starting from its current content:
  `python3 tools/eject.py gameplay/items/tms.html`
- Take over EVERY template page at once: `python3 tools/eject.py --all-static`
- Hand a page back to the generators: delete its file from here.
- Files contain only the page BODY (no <html>/<head>/sidebar) — plain HTML,
  same classes as everywhere else (.callout, .card, .bevel, tables,
  .img-frame, .img-peek all work).

Already hand-written: gameplay/items/crafting.html
