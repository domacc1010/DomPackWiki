# assets/data

| File | Edit by hand? |
|---|---|
| `pokemon-custom.json` | **YES — this is yours.** Never touched by the build scripts. |
| `pokemon.json` | No — regenerated from the datapacks on every build. |
| `search-index.json` | No — regenerated on every build. |

## pokemon-custom.json — customize any Pokémon's card

Add an entry keyed by the Pokémon's slug (lowercase, same as the `?mon=`
value in the Pokédex URL). Changes appear on page refresh — **no rebuild
needed**. All fields optional:

```json
"charizard": {
  "name":  "Charizard (Server Ace)",
  "image": "../../assets/images/pokemon/charizard-shiny.png",
  "note":  "Short highlighted callout under the header.",
  "sections": [
    { "title": "Where to find it here",
      "html": "<p>Any HTML: text, <b>bold</b>, images, links, tables…</p>" },
    { "title": "Drops", "html": "<ul><li>…</li></ul>" }
  ],
  "hide_spawns": false,
  "hide_stats": false
}
```

- `sections` is the main tool — add as many as you want, each becomes a
  heading + your HTML on the card, after the auto-generated parts.
- `hide_spawns` / `hide_stats`: set `true` to remove the auto blocks
  entirely and write your own version in a section instead.
- Image paths are relative to `gameplay/pokemon/index.html`, so
  `../../assets/images/...` reaches the images folder.
- Keep the JSON valid (quotes around keys, commas between entries) — if the
  file has a syntax error the Pokédex just ignores it and shows stock cards.
