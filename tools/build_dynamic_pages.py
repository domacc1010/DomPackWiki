#!/usr/bin/env python3
"""
build_site.py — (re)builds the wiki pages that are driven by extracted
datapack data. Static template pages (FAQ, server rules, getting-started,
etc.) already exist in the site and aren't touched by this script.

Run order:
    1. python3 tools/extract_data.py /path/to/datapacks
    2. python3 tools/build_site.py

If a tools/data/*.json file is missing (extractor hasn't been run, or that
category no longer exists in the datapacks), the matching page falls back
to a blank fill-in template instead of crashing, so this is always safe to
run even with partial data.
"""
import json, os, sys, glob, re
import html as html_lib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from site_common import write_page, fill, basic_guide_page, SITE_ROOT, clean_pokemon_name, BUILD_STAMP, img_peek  # noqa: E402

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def load(name):
    path = os.path.join(DATA_DIR, name)
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

TIER_LABELS = {
    "TIER_ONE": "1★", "TIER_TWO": "2★", "TIER_THREE": "3★", "TIER_FOUR": "4★",
    "TIER_FIVE": "5★", "TIER_SIX": "6★", "TIER_SEVEN": "7★",
}
TIER_ORDER = ["TIER_ONE","TIER_TWO","TIER_THREE","TIER_FOUR","TIER_FIVE","TIER_SIX","TIER_SEVEN"]

def title_species(slug):
    return clean_pokemon_name(slug)

# =================================================================
# RAIDS  ->  gameplay/mechanics/raids.html
# =================================================================
def build_raids_page():
    data = load("raids.json")
    if not data:
        write_page("gameplay/mechanics/raids.html", "Raids", basic_guide_page("Raids"),
            crumb='<a href="../../index.html">Home</a> / Mechanics / Raids')
        print("  raids.html -> placeholder (no raids.json)")
        return

    bosses = data.get("bosses", [])
    modifiers = data.get("modifiers", [])

    by_tier = {}
    for b in bosses:
        by_tier.setdefault(b["tier"], []).append(b)

    tier_sections = ""
    for tier in TIER_ORDER:
        rows = by_tier.get(tier, [])
        if not rows:
            continue
        rows_sorted = sorted(rows, key=lambda r: r["species"] or "")
        trs = ""
        for r in rows_sorted:
            props = ", ".join(f'{p["name"]}={p["value"]}' for p in r.get("custom_properties", []))
            trs += (f'<tr><td>{title_species(r["species"] or r["slug"])}</td>'
                    f'<td>{r["type"].title() if r["type"] else ""}</td>'
                    f'<td class="mono">{r["weight"]}</td>'
                    f'<td class="mono">{props}</td></tr>')
        tier_sections += f"""
        <h3>{TIER_LABELS.get(tier, tier)} Raids <span class="badge">{len(rows)} bosses</span></h3>
        <table><tr><th>Pokémon</th><th>Type</th><th>Spawn Weight</th><th>Notes</th></tr>{trs}</table>
        """

    mod_rows = "".join(
        f'<tr><td>{m["feature"]}</td><td>{(m["type"] or "").title()}</td><td class="mono">{m["weight"]}</td></tr>'
        for m in sorted(modifiers, key=lambda m: (m["feature"] or "", m["type"] or ""))
    )

    content = f"""
    <div class="callout"><strong>Auto-generated</strong> from <code>cobblemonraiddens</code> —
    re-run <code>tools/extract_data.py</code> then <code>tools/build_site.py</code> after any raid den update.</div>
    <h2>What is it?</h2>{fill("2-3 sentence explainer of how raid dens work on this server.")}
    <h2>Where do I find it?</h2>{fill("How players locate/trigger a raid den in-world.")}
    <h2>Raid Tiers</h2>
    <p>{len(bosses)} raid bosses currently configured, grouped by star tier. Higher tiers are rarer and tougher.</p>
    {tier_sections}
    <h2>Special Raid Modifiers</h2>
    <p>Tera, Dynamax/Gigantamax, and Stellar modifiers that can appear on top of a normal boss roll.</p>
    <table><tr><th>Feature</th><th>Type</th><th>Weight</th></tr>{mod_rows}</table>
    <h2>Tips &amp; Strategies</h2>
    <ul class="tasks"><li>{fill("Tip one")}</li><li>{fill("Tip two")}</li></ul>
    """
    write_page("gameplay/mechanics/raids.html", "Raids", content,
        crumb='<a href="../../index.html">Home</a> / Mechanics / Raids',
        lede=f"{len(bosses)} bosses across {len([t for t in TIER_ORDER if by_tier.get(t)])} tiers — pulled straight from the raid den datapack.")
    print(f"  raids.html -> {len(bosses)} bosses, {len(modifiers)} modifiers")

# =================================================================
# STRUCTURES + LEGENDARY MONUMENTS + BIOMES
#   -> gameplay/world/structures.html
#   -> gameplay/world/legendary-monuments.html
#   -> gameplay/world/biomes.html
# =================================================================
# Landmark structures that are legendary encounter sites, named after the
# location rather than the Pokémon. Grounded in the pack's own lumymon radar
# recipes (e.g. necrozma_dawn_radar, space_time_radar, calyrex_ice_radar)
# plus Pokémon canon for the location names.
LANDMARK_LEGENDS = {
    "bell_tower": "Ho-Oh",
    "burned_tower": "Raikou / Entei / Suicune",
    "whirl_island": "Lugia",
    "celebi_shrine": "Celebi",
    "sky_pillar": "Rayquaza",
    "dyna_tree": "Galarian Articuno / Zapdos / Moltres",
    "secret_garden": "Latias / Latios",
    "spear_pillar": "Dialga / Palkia",
    "fullmoon_island": "Cresselia",
    "crescent_isle": "Darkrai",
    "flower_paradise": "Shaymin",
    "snowpoint_temple": "Regigigas",
    "split_decision_temple": "Regieleki / Regidrago",
    "crown_cemetery": "Spectrier (Calyrex)",
    "crown_spire": "Calyrex / Glastrier",
    "dawn_tower": "Necrozma (Dawn Wings)",
    "dusk_tower": "Necrozma (Dusk Mane)",
    "eterna_building": "Rotom",
    "wind_plant": "Heatran",
}
VILLAIN_STRUCTURES = {"team_rocket_tower", "rocket_radio_tower", "team_galactic_hq"}
REGION_ORDER = ["Kanto", "Johto", "Hoenn", "Sinnoh"]

STRUCTURE_TRAINER_ALIASES = {
    ("Hoenn", "tell_pat"): "tell",  # shared gym — structure file covers both Tell and Pat
}

def _load_structures_categorized():
    """Returns structures.json rows with category refined to
    gym / league / legendary / mythical / legendary-landmark / villain / landmark,
    plus the matching trainer (for gyms)."""
    structures = load("structures.json") or []
    trainers = load("trainers.json") or []
    trainer_by_key = {}
    for t in trainers:
        parts = t["slug"].split("_", 1)
        if len(parts) == 2:
            trainer_by_key[(t["region"], parts[1])] = t
    for s in structures:
        lookup_name = STRUCTURE_TRAINER_ALIASES.get((s["region"], s["name"]), s["name"])
        t = trainer_by_key.get((s["region"], lookup_name))
        if s["category"] == "other":
            if s["name"] in VILLAIN_STRUCTURES:
                s["category"] = "villain"
            elif s["name"] in LANDMARK_LEGENDS:
                s["category"] = "legendary-landmark"
                s["legendary"] = LANDMARK_LEGENDS[s["name"]]
            elif t and t["rank"] == "Gym Leader":
                s["category"] = "gym"
            else:
                s["category"] = "landmark"
        s["trainer"] = {"name": t["name"], "rank": t["rank"], "slug": t["slug"],
                        "level_range": t.get("level_range")} if t else None
    return structures

def _structure_label(name):
    return name.replace("_", " ").title().replace("Ltsurge", "Lt. Surge").replace("Tell Pat", "Tell & Pat")

def _dim_badge(dim):
    return f' <span class="badge">{dim}</span>' if dim != "Overworld" else ""

def build_structures_page():
    structures = _load_structures_categorized()
    if not structures:
        write_page("gameplay/world/structures.html", "Structures", basic_guide_page("Structures"),
            crumb='<a href="../../index.html">Home</a> / World / Structures')
        print("  structures.html -> placeholder (no structures.json)")
        return

    region_sections = ""
    for region in REGION_ORDER:
        rows = [s for s in structures if s["region"] == region]
        if not rows:
            continue
        gyms = sorted([s for s in rows if s["category"] == "gym"], key=lambda s: s["name"])
        leagues = [s for s in rows if s["category"] == "league"]
        villains = [s for s in rows if s["category"] == "villain"]
        landmarks = sorted([s for s in rows if s["category"] == "landmark"], key=lambda s: s["name"])

        gym_trs = ""
        for s in gyms:
            t = s["trainer"]
            lvl = f'Lv {t["level_range"][0]}\u2013{t["level_range"][1]}' if t and t.get("level_range") else ""
            leader = (f'<a href="../trainers/{region.lower()}.html#trainer-{t["slug"]}">{t["name"]}</a>'
                      if t else _structure_label(s["name"]))
            gym_trs += (f'<tr><td>{_structure_label(s["name"])}\u2019s Gym{_dim_badge(s["dimension"])}</td>'
                        f'<td>{leader}</td><td>{s["biome"]}</td><td class="mono">{lvl}</td>'
                        f'<td class="mono">{s["spacing"] or "?"} / {s["separation"] or "?"}</td></tr>')

        other_trs = ""
        for s in leagues + villains + landmarks:
            kind = {"league": "Pokémon League", "villain": "Villain Base", "landmark": "Landmark"}[s["category"]]
            other_trs += (f'<tr><td>{_structure_label(s["name"])}{_dim_badge(s["dimension"])}</td>'
                          f'<td>{kind}</td><td>{s["biome"]}</td>'
                          f'<td class="mono">{s["spacing"] or "?"} / {s["separation"] or "?"}</td></tr>')

        region_sections += f"""
        <h2>{region} <span class="badge">{len(rows)} structures</span></h2>
        <h3>Gyms</h3>
        <table><tr><th>Structure</th><th>Leader</th><th>Biome</th><th>Levels</th><th>Spacing / Sep.</th></tr>{gym_trs}</table>
        <h3>League, Villain Bases &amp; Landmarks</h3>
        <table><tr><th>Structure</th><th>Type</th><th>Biome</th><th>Spacing / Sep.</th></tr>{other_trs}</table>
        <p>Legendary and mythical monuments for {region} are listed on the
        <a href="legendary-monuments.html">Legendary Monuments</a> page.</p>
        """

    n_gyms = sum(1 for s in structures if s["category"] == "gym")
    content = f"""
    <div class="callout"><strong>Auto-generated</strong> from every region pack's
    <code>worldgen/structure</code> + <code>structure_set</code> files — real biomes, dimensions, and
    placement rarity. Spacing/Separation are vanilla placement values in chunks; higher spacing = rarer.
    Gym leader links jump to that leader's full team.</div>
    <h2>How structures work in CobbleVerse</h2>
    <p>Each gym is a real building that generates naturally in one specific biome — track them down with
    <a href="../server-features/lumymon.html">LumyMon treasure maps</a> from each region's Cartographer.
    Note the dimension badges: some gyms generate in the <strong>Nether</strong>, and every regional League
    generates in <strong>The End</strong>, so those fights come with a journey attached.</p>
    {region_sections}
    <h2>Base Cobblemon structures</h2>
    <p>On top of the CobbleVerse buildings above, the Cobblemon mod itself generates several structure
    families throughout the world (full details on the
    <a href="https://wiki.cobblemon.com/index.php/Structure">official Cobblemon wiki</a>):</p>
    <div class="card-grid">
      <div class="card bevel"><h3>Fossil Dig Sites</h3><p>23 "Prehistoric" archaeology structures (fallen trees,
      frozen ponds, hydrothermal vents, mud pits…), each blending into its biome. Brush their Suspicious
      Sand/Gravel for <a href="../items/fossils.html">Fossils</a>, held items, evolution stones, and herbs —
      each variant has one guaranteed-fossil block.</p></div>
      <div class="card bevel"><h3>Ruins</h3><p>Gimmighoul-themed ruins containing Gilded Chests and ancient
      Relic Coin treasure. The place to start a Gimmighoul \u2192 Gholdengo hunt.</p></div>
      <div class="card bevel"><h3>Mini Dungeons</h3><p>Compact dungeons built around vanilla Trial Spawners,
      with Pokémon-themed loot.</p></div>
      <div class="card bevel"><h3>Village Structures</h3><p>Pokécenters and Pokémon-themed buildings that
      generate inside villages — CobbleVerse extends these with its own variants for every village biome
      (badlands, cherry, jungle, swamp, mushroom and more).</p></div>
    </div>
    <h2>Tips &amp; Strategies</h2>
    <ul class="tasks"><li>{fill("Which map mods (Xaero's) mark these structures, and how")}</li>
    <li>{fill("Server-specific tips — e.g. is structure locating via commands allowed?")}</li></ul>
    """
    write_page("gameplay/world/structures.html", "Structures", content,
        crumb='<a href="../../index.html">Home</a> / World / Structures',
        lede=f"{len(structures)} CobbleVerse structures across {len(REGION_ORDER)} regions — {n_gyms} gyms, league buildings, villain bases, landmarks — plus the base Cobblemon structure families.")
    print(f"  structures.html -> {len(structures)} structures ({n_gyms} gyms)")

def build_legendary_monuments_page():
    structures = _load_structures_categorized()
    sites = [s for s in structures if s["category"] in ("legendary", "mythical", "legendary-landmark")]
    if not sites:
        write_page("gameplay/world/legendary-monuments.html", "Legendary Monuments", basic_guide_page("Legendary Monuments"),
            crumb='<a href="../../index.html">Home</a> / World / Legendary Monuments')
        print("  legendary-monuments.html -> placeholder (no structures.json)")
        return

    mons = load("pokemon.json") or []
    slug_to_dex = {m["slug"]: m["dex"] for m in mons if m.get("dex")}

    region_sections = ""
    for region in REGION_ORDER:
        rows = [s for s in sites if s["region"] == region]
        if not rows:
            continue
        trs = ""
        for s in sorted(rows, key=lambda s: (s["category"], s["name"])):
            img_base = f'../../assets/images/LenMonu/{s["name"]}'
            if s["category"] in ("legendary", "mythical"):
                pkmn = clean_pokemon_name(s["name"])
                dex = slug_to_dex.get(s["name"])
                img = (f'<img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{dex}.png" '
                       f'alt="{pkmn}" width="32" height="32" style="image-rendering:pixelated;vertical-align:middle;margin-right:6px;">'
                       if dex else "")
                pokemon_cell = (f'{img}<a href="../pokemon/index.html?mon={s["name"]}">{pkmn}</a>' if dex else pkmn)
                site_cell = img_peek(f'{pkmn}\u2019s Monument', img_base)
                cat = s["category"].title()
            else:
                pokemon_cell = s["legendary"]
                site_cell = img_peek(_structure_label(s["name"]), img_base)
                cat = "Landmark Site"
            trs += (f'<tr><td>{site_cell}{_dim_badge(s["dimension"])}</td><td>{pokemon_cell}</td>'
                    f'<td>{cat}</td><td>{s["biome"]}</td>'
                    f'<td class="mono">{s["spacing"] or "?"} / {s["separation"] or "?"}</td></tr>')
        region_sections += f"""
        <h3>{region} <span class="badge">{len(rows)} sites</span></h3>
        <table><tr><th>Site</th><th>Pokémon</th><th>Type</th><th>Biome</th><th>Spacing / Sep.</th></tr>{trs}</table>
        """

    n_landmark = sum(1 for s in sites if s["category"] == "legendary-landmark")
    content = f"""
    <div class="callout"><strong>Auto-generated</strong> from every region pack's worldgen files —
    now covering all four regions, including named landmark sites (Sky Pillar, Spear Pillar, Bell Tower…)
    that previous versions of this page missed. Landmark\u2192Pokémon associations are grounded in the pack's
    own radar-crafting recipes plus Pokémon canon; confirm any you're unsure of in-game.</div>
    <h2>What is it?</h2>
    <p>Legendary and Mythical Pokémon in CobbleVerse each guard a unique structure that generates naturally
    in the world, rather than only spawning via events. Spacing/Separation are vanilla structure-placement
    values (in chunks) — higher spacing means rarer. Watch the dimension badges: some sites are in the
    Nether or The End.</p>
    <h2>How do I find them?</h2>
    <p>Two tools, both from <a href="../server-features/lumymon.html">LumyMon</a>: craftable
    <strong>radar items</strong> tuned to a specific legendary (about 30 recipes across the regions), and
    <strong>Cartographer treasure maps</strong> that point straight at gyms and league towers to get you
    into the right area.</p>
    <div class="callout"><strong>Note on regions below:</strong> groupings reflect which datapack/build
    area a site is bundled into on this server, not always the Pokémon's mainline-game region — Calyrex
    and Necrozma's sites are bonus content tucked into the Kanto-area files rather than native to Kanto.</div>
    <p><span class="img-peek" data-img-base="../../assets/images/LenMonu/articuno">Hover any site name
    with a dotted underline</span> to see a screenshot of the structure; hover the preview to enlarge it,
    click it to open full-size. Previews load from <code>assets/images/LenMonu/</code> — drop in a
    screenshot named after the site (e.g. <code>sky_pillar.png</code>) and it appears automatically,
    no rebuild needed.</p>
    {region_sections}
    <h2>Tips &amp; Strategies</h2>
    <ul class="tasks"><li>{fill("Recommended progression — which legendaries are realistic early vs late game")}</li>
    <li>{fill("Any server rules about legendary claims/camping")}</li></ul>
    <h2>Related Pages</h2>
    <p><a href="structures.html">All structures</a> · <a href="../mechanics/raids.html">Raids</a> (several
    legendaries also appear as raid bosses) · <a href="../items/mega-evolution.html">Mega Evolution</a></p>
    """
    write_page("gameplay/world/legendary-monuments.html", "Legendary Monuments", content,
        crumb='<a href="../../index.html">Home</a> / World / Legendary Monuments',
        lede=f"{len(sites)} legendary/mythical sites across all 4 regions — {len(sites) - n_landmark} dedicated monuments + {n_landmark} named landmark sites.")
    print(f"  legendary-monuments.html -> {len(sites)} sites across 4 regions")

def build_biomes_page():
    mons = load("pokemon.json") or []
    if not mons:
        write_page("gameplay/world/biomes.html", "Biomes", basic_guide_page("Biomes"),
            crumb='<a href="../../index.html">Home</a> / World / Biomes')
        print("  biomes.html -> placeholder (no pokemon.json)")
        return

    biome_counts = {}
    biome_examples = {}
    for m in mons:
        seen = set()
        for sp in m.get("spawns", []):
            for b in sp.get("biomes", []):
                if b in seen:
                    continue
                seen.add(b)
                biome_counts[b] = biome_counts.get(b, 0) + 1
                biome_examples.setdefault(b, [])
                if len(biome_examples[b]) < 8:
                    biome_examples[b].append(m["name"])

    top = sorted(biome_counts.items(), key=lambda kv: -kv[1])[:30]
    trs = "".join(
        f'<tr><td>{b}</td><td class="mono">{n}</td>'
        f'<td class="mono">{", ".join(biome_examples[b][:6])}\u2026</td></tr>'
        for b, n in top
    )

    structures = _load_structures_categorized()
    terralith_structs = [s for s in structures if s.get("biome_raw") and "terralith" in s["biome_raw"]]

    content = f"""
    <div class="callout"><strong>Auto-generated</strong> from the spawn data of all {len(mons)} species —
    this table counts how many different Pokémon can spawn in each biome group, straight from this
    server's datapacks.</div>
    <h2>How biomes work here</h2>
    <p>Cobblemon assigns spawns to <em>biome tags</em> (groups like "is_jungle" or "is_freezing") rather than
    single biomes, so one row below usually covers several vanilla and Terralith biomes at once. Rarity,
    time-of-day, weather, and light conditions then narrow down what actually appears — check any species
    in the <a href="../pokemon/index.html">Pokédex</a> for its exact conditions.</p>
    <h2>Terralith</h2>
    <p>This pack ships <strong>Terralith</strong> world generation as a datapack, adding nearly a hundred
    new overworld biomes. They matter for more than scenery: {len(terralith_structs)} CobbleVerse structures
    generate exclusively in Terralith biomes (for example
    {', '.join(_structure_label(s['name']) + ' in ' + s['biome'] for s in terralith_structs[:3])}\u2026),
    so learning the new biomes pays off directly when structure-hunting.</p>
    <h2>Most Pokémon-rich biome groups</h2>
    <table><tr><th>Biome group</th><th># Species</th><th>Examples</th></tr>{trs}</table>
    <h2>Special spawn conditions worth knowing</h2>
    <ul class="tasks">
      <li>Hundreds of spawns are day-only or night-only — the same forest has a different cast after dark.</li>
      <li>Some species only appear in rain or thunder, at specific heights (deep caves vs mountain peaks),
      near specific blocks, inside structures, or in slime chunks.</li>
      <li>Fishing spawns depend on rod, bait, and lure level — roughly 600 spawn entries are fishing-based.</li>
    </ul>
    <h2>Tips &amp; Strategies</h2>
    <ul class="tasks"><li>{fill("Best early-game biomes to settle near on this server's world")}</li>
    <li>{fill("Where players have actually found rare biomes on the live map")}</li></ul>
    """
    write_page("gameplay/world/biomes.html", "Biomes", content,
        crumb='<a href="../../index.html">Home</a> / World / Biomes',
        lede=f"Which biomes hold the most Pokémon — computed from all {len(mons)} species' real spawn data.")
    print(f"  biomes.html -> {len(biome_counts)} biome groups from spawn data")

# =================================================================
# TM RECIPES  ->  gameplay/items/tms.html
# =================================================================
DISC_LABELS = {
    "copper_blank_disc": "Copper", "iron_blank_disc": "Iron", "gold_blank_disc": "Gold",
    "emerald_blank_disc": "Emerald", "diamond_blank_disc": "Diamond", "netherite_blank_disc": "Netherite",
    "unknown": "Other / Special",
}

def build_tms_page():
    recipes = load("tm_recipes.json")
    if not recipes:
        write_page("gameplay/items/tms.html", "TM Crafting", basic_guide_page("TM Crafting"),
            crumb='<a href="../../index.html">Home</a> / Items / TM Crafting')
        print("  tms.html -> placeholder (no tm_recipes.json)")
        return

    by_disc = {}
    for r in recipes:
        by_disc.setdefault(r["disc"] or "unknown", []).append(r)

    sections = ""
    for disc, label in DISC_LABELS.items():
        rows = by_disc.get(disc, [])
        if not rows:
            continue
        trs = "".join(
            f'<tr><td>{r["move"].replace("_"," ").title()}</td>'
            f'<td class="mono">{", ".join(i.replace("cobblemon:","").replace("minecraft:","").replace("_"," ") for i in r["ingredients"])}</td></tr>'
            for r in sorted(rows, key=lambda r: r["move"])
        )
        sections += f"""
        <h3>{label} Tier <span class="badge">{len(rows)} TMs</span></h3>
        <table><tr><th>Move</th><th>Other Ingredients (+ {label} Blank Disc)</th></tr>{trs}</table>
        """

    content = f"""
    <div class="callout"><strong>Auto-generated</strong> from <code>tmcraft/recipe</code> — {len(recipes)} TM
    recipes total. Re-run the extractor after any TM balance pass.</div>
    <h2>What is it?</h2>
    <p>TMs are crafted, not found — each one needs a tier-appropriate blank disc plus move-specific
    ingredients (usually a type gem and a themed item).</p>
    <h2>Where do I find blank discs?</h2>{fill("Where players get Copper/Iron/Emerald/Diamond/Netherite blank discs.")}
    {sections}
    """
    write_page("gameplay/items/tms.html", "TM Crafting", content,
        crumb='<a href="../../index.html">Home</a> / Items / TM Crafting',
        lede=f"{len(recipes)} craftable TMs across {len(by_disc)} disc tiers.")
    print(f"  tms.html -> {len(recipes)} recipes across {len(by_disc)} tiers")

# =================================================================
# FOSSILS  ->  gameplay/items/fossils.html
# =================================================================
def build_fossils_page():
    fossils = load("fossils.json")
    if not fossils:
        write_page("gameplay/items/fossils.html", "Fossils", basic_guide_page("Fossils"),
            crumb='<a href="../../index.html">Home</a> / Items / Fossils')
        print("  fossils.html -> placeholder (no fossils.json)")
        return

    trs = "".join(
        f'<tr><td>{title_species(f["result"])}</td>'
        f'<td class="mono">{", ".join(i.replace("lumymon:","").replace("cobblemon:","").replace("_"," ") for i in f["fossils"])}</td></tr>'
        for f in sorted(fossils, key=lambda f: f["result"] or "")
    )
    content = f"""
    <div class="callout"><strong>Auto-generated</strong> from <code>cobblemon/fossils</code> —
    re-run the extractor after any fossil revival changes.</div>
    <h2>What is it?</h2>
    <p>Fossil items can be restored into their living Pokémon at a Fossil Machine / Revival Machine.</p>
    <h2>Restoration Table</h2>
    <table><tr><th>Result</th><th>Required Fossil Item(s)</th></tr>{trs}</table>
    <h2>Where do I find fossils?</h2>{fill("Dig sites, loot tables, or purchase locations.")}
    <h2>Tips &amp; Strategies</h2><ul class="tasks"><li>{fill("Tip")}</li></ul>
    """
    write_page("gameplay/items/fossils.html", "Fossils", content,
        crumb='<a href="../../index.html">Home</a> / Items / Fossils',
        lede=f"{len(fossils)} fossil combinations currently configured.")
    print(f"  fossils.html -> {len(fossils)} fossils")

# =================================================================
# LUMYMON  ->  gameplay/server-features/lumymon.html
# =================================================================
def build_lumymon_page():
    npcs = load("lumymon_maps.json")
    if not npcs:
        write_page("gameplay/server-features/lumymon.html", "LumyMon", basic_guide_page("LumyMon"),
            crumb='<a href="../../index.html">Home</a> / Server Features / LumyMon')
        print("  lumymon.html -> placeholder (no lumymon_maps.json)")
        return

    total_trades = sum(len(n["trades"]) for n in npcs)
    sections = ""
    for n in sorted(npcs, key=lambda n: n["region"]):
        trs = "".join(
            f'<tr><td>{(t["display_name"] or t["destination"] or "").strip()}</td>'
            f'<td class="mono">{(t["tome"] or "").replace("lumymon:","").replace("_"," ")}</td></tr>'
            for t in n["trades"]
        )
        sections += f"""
        <h3>{n["region"]} Cartographer <span class="badge">{len(n["trades"])} maps</span></h3>
        <table><tr><th>Destination</th><th>Tome / Trade Item Required</th></tr>{trs}</table>
        """

    content = f"""
    <div class="callout"><strong>Original content</strong> — no external wiki documents LumyMon.
    <strong>Auto-generated</strong> from <code>lumymon/trades</code> — {total_trades} treasure map trades
    across {len(npcs)} regional cartographers.</div>
    <h2>What is it?</h2>
    <p>LumyMon adds Cartographer NPCs (one per region) who trade themed "tome" items for treasure maps
    pointing straight at gym leaders, legendary sites, and league towers.</p>
    <h2>Where do I find it?</h2>{fill("Where each regional Cartographer NPC is physically located.")}
    <h2>How do I use it?</h2>
    <p>Bring the NPC the tome item shown below (plus a vanilla map) to buy a treasure map to that destination.</p>
    {sections}
    <h2>Radar Items</h2>
    <p>LumyMon also crafts "radar" items for tracking specific legendaries — see the crafting recipes in
    <code>lumymon/recipe</code> for the full list (not yet auto-extracted here).</p>
    {fill("Document radar crafting recipes once you're ready to extend the extractor.")}
    <h2>Tips &amp; Strategies</h2><ul class="tasks"><li>{fill("Tip")}</li></ul>
    """
    write_page("gameplay/server-features/lumymon.html", "LumyMon", content,
        crumb='<a href="../../index.html">Home</a> / Server Features / LumyMon',
        lede=f"{total_trades} treasure-map trades across {len(npcs)} regions — Kanto, Johto, Hoenn, Sinnoh.")
    print(f"  lumymon.html -> {len(npcs)} cartographers, {total_trades} trades")

# =================================================================
# POKÉMON  ->  gameplay/pokemon/index.html  (Cobbledex-style app)
# =================================================================
def _trim(d):
    """Drop null/empty values so the shipped JSON stays lean."""
    if isinstance(d, dict):
        out = {}
        for k, v in d.items():
            v2 = _trim(v)
            if v2 in (None, [], {}, ""):
                continue
            out[k] = v2
        return out
    if isinstance(d, list):
        return [_trim(x) for x in d]
    return d

def build_pokedex_page():
    mons = load("pokemon.json")
    if not mons:
        write_page("gameplay/pokemon/index.html", "Pokémon", basic_guide_page("Pokémon"),
            crumb='<a href="../../index.html">Home</a> / Pokémon')
        print("  pokemon/index.html -> placeholder (no pokemon.json)")
        return

    trimmed = [_trim(m) for m in mons]
    data_dir = os.path.join(SITE_ROOT, "assets", "data")
    os.makedirs(data_dir, exist_ok=True)
    with open(os.path.join(data_dir, "pokemon.json"), "w", encoding="utf-8") as f:
        json.dump(trimmed, f, separators=(",", ":"), ensure_ascii=False)

    bucket_counts = {}
    for m in mons:
        b = m.get("best_bucket") or "unknown"
        bucket_counts[b] = bucket_counts.get(b, 0) + 1

    content = f"""
    <div class="callout"><strong>Auto-generated</strong> from <code>cobblemon/spawn_pool_world</code> —
    every one of the {len(mons)} species currently spawnable in CobbleVerse, with real biome/rarity/level/
    time/weather conditions pulled straight from the server's datapacks. Type, ability and base-stat data
    streams in live from PokeAPI in the background (cached in your browser) so this page never goes stale
    and never ships a multi-megabyte hand-maintained stat table. Click any card for the full entry.</div>
    <p class="mono" style="font-size:.75rem;">Rarity mix — common {bucket_counts.get('common',0)} ·
    uncommon {bucket_counts.get('uncommon',0)} · rare {bucket_counts.get('rare',0)} ·
    ultra-rare {bucket_counts.get('ultra-rare',0)}</p>

    <div data-pokedex-root data-pokemon-json="../../assets/data/pokemon.json">
      <div class="dex-toolbar">
        <input class="dex-search" type="search" placeholder="Search by name or dex number…" aria-label="Search Pokémon">
        <span class="dex-count"></span>
        <div class="dex-progress"></div>
        <div class="dex-chip-row rarities" aria-label="Filter by rarity"></div>
        <div class="dex-chip-row gens" aria-label="Filter by generation"></div>
        <div class="dex-chip-row types" aria-label="Filter by type"></div>
      </div>
      <div class="dex-grid"><div class="dex-empty">Loading Pokédex…</div></div>
    </div>

    <h2>Building Out Individual Pages</h2>
    <p>This directory covers every spawnable species with live data. If you want to hand-write deeper
    server-specific pages for a handful of standout Pokémon (signature raid bosses, gym aces, community
    favorites), copy the template below into its own file and link it from here — the same pattern the
    old one-page-per-Pokémon workflow used.</p>
    <div class="bevel card">
    <h3>{{Pokémon Name}}<span class="badge">TEMPLATE</span></h3>
    <h4>Breeding</h4><div class="fill">Egg group(s), compatible species</div>
    <h4>Drops</h4><div class="fill">Item drop table</div>
    <h4>Competitive</h4><div class="fill">Best nature, EV/IV build, common movesets</div>
    <h4>Trivia &amp; Gallery</h4><div class="fill">Fun facts + screenshots (drop images in /assets)</div>
    </div>
    """
    write_page("gameplay/pokemon/index.html", "Pokémon", content,
        crumb='<a href="../../index.html">Home</a> / Pokémon',
        lede=f"{len(mons)} spawnable species · search, filter by type/generation/rarity, click a card for full detail.")

    # The Trainers page links back here with ?mon=slug — the modal backdrop needs
    # to exist in the DOM once; site_common's shared template doesn't carry it,
    # so splice it into the page we just wrote.
    path = os.path.join(SITE_ROOT, "gameplay/pokemon/index.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    modal_html = ('<div class="dex-modal-backdrop"><div class="dex-modal"></div></div>\n'
                  f'<script src="../../assets/js/pokedex.js?v={BUILD_STAMP}"></script>\n</body>')
    html = html.replace("</body>", modal_html)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  pokemon/index.html -> {len(mons)} species (Pokédex app)")

# =================================================================
# TRAINERS & GYMS  ->  gameplay/trainers/*.html
# =================================================================
RANK_ORDER = ["Gym Leader", "Elite Four", "Champion", "Rival", "Trainer",
              "Story NPC", "LumyMon NPC", "Custom Trainer"]

def _slug_to_dex(mons):
    return {m["slug"]: m["dex"] for m in mons if m.get("dex")}

def _mon_sprite_tag(species_slug, slug_to_dex, level=None, size="small"):
    dex = slug_to_dex.get(species_slug)
    src = (f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{dex}.png"
           if dex else "")
    label = clean_pokemon_name(species_slug)
    lvl = f'<span class="lvl">Lv{level}</span>' if level else ""
    img = (f'<img src="{src}" alt="{label}" loading="lazy" onerror="this.style.visibility=\'hidden\'">'
           if src else "")
    href = f'../pokemon/index.html?mon={species_slug}'
    return (f'<a class="team-mon" href="{href}" title="{label}">{img}'
            f'<span>{label}</span>{lvl}</a>')

def _trainer_card_html(t, slug_to_dex, rank_class="rank-pill"):
    team_html = "".join(_mon_sprite_tag(p["species"], slug_to_dex, p.get("level")) for p in t["team"])
    bag = ", ".join(f'{b["item"]} ×{b["quantity"]}' for b in t.get("bag", []) if b.get("item"))
    biomes = ", ".join(t.get("biomes", []))
    meta_bits = [f'{t["team_count"]} Pokémon']
    if t.get("level_range"):
        lo, hi = t["level_range"]
        meta_bits.append(f'Lv {lo}\u2013{hi}' if lo != hi else f'Lv {lo}')
    if t.get("battle_format"):
        meta_bits.append(t["battle_format"].replace("_", " ").title())
    if biomes:
        meta_bits.append(f'Found in: {biomes}')
    if bag:
        meta_bits.append(f'Bag: {bag}')
    return f"""
    <div class="trainer-card" id="trainer-{t['slug']}">
      <div class="trainer-head"><h3>{t['name']}</h3><span class="{rank_class}">{t['rank']}</span></div>
      <div class="trainer-meta">{' · '.join(meta_bits)}</div>
      <div class="team-row">{team_html}</div>
    </div>
    """

def build_trainers_index(trainers):
    by_region = {}
    for t in trainers:
        if t.get("org"):
            continue
        by_region.setdefault(t["region"], []).append(t)
    region_order = ["Kanto", "Johto", "Hoenn", "Sinnoh", "Hisui"]
    region_cards = ""
    for r in region_order:
        rows = by_region.get(r, [])
        if not rows:
            continue
        leaders = sum(1 for t in rows if t["rank"] == "Gym Leader")
        e4 = sum(1 for t in rows if t["rank"] == "Elite Four")
        champs = sum(1 for t in rows if t["rank"] == "Champion")
        slug = r.lower()
        blurb = f"{leaders} Gym Leaders" if leaders else f"{len(rows)} Trainers"
        if e4:
            blurb += f", {e4} Elite Four"
        if champs:
            blurb += f", {champs} Champion"
        region_cards += f"""
        <div class="bevel card">
          <h3>{r}</h3><p>{blurb}</p>
          <p><a href="{slug}.html">View {r} Trainers →</a></p>
        </div>"""

    villain_count = sum(1 for t in trainers if t.get("org"))
    orgs = sorted(set(t["org"] for t in trainers if t.get("org")))
    content = f"""
    <div class="callout"><strong>Auto-generated</strong> from <code>rctmod/trainers</code> (the Roaming
    Cobblemon Trainers datapack) — {len(trainers)} named trainers with real teams: species, level, moves,
    nature, ability, held items and IV/EV spreads, exactly as configured on this server.</div>
    <h2>What is it?</h2>
    <p>CobbleVerse trainers roam the overworld and challenge you to a battle when you get close. Each
    region has its own Gym Leaders, Elite Four, and Champion, styled after the mainline games — plus
    rivals, story NPCs, and full villainous team rosters.</p>
    <h2>Regions</h2>
    <div class="card-grid">{region_cards}</div>
    <h2>Villainous Teams</h2>
    <div class="bevel card">
      <h3>Team Rocket, Team Galactic &amp; more<span class="badge">{villain_count} trainers</span></h3>
      <p>{', '.join(orgs)} — bosses, admins, and rank-and-file grunts.</p>
      <p><a href="villains.html">View Villainous Teams →</a></p>
    </div>
    <h2>Other Notable Trainers</h2>
    <p><a href="other.html">Rivals, LumyMon NPCs, and custom trainers →</a></p>
    <h2>Tips &amp; Strategies</h2>
    <ul class="tasks"><li>{fill("How players actually encounter a roaming trainer in-world")}</li>
    <li>{fill("What happens on a rematch / cooldown")}</li></ul>
    """
    write_page("gameplay/trainers/index.html", "Trainers & Gyms", content,
        crumb='<a href="../../index.html">Home</a> / Trainers & Gyms',
        lede=f"{len(trainers)} trainers extracted straight from the server's roaming-trainer datapack.")

def build_trainers_region_page(region, trainers):
    rows = [t for t in trainers if t["region"] == region and not t.get("org")]
    if not rows:
        return
    slug_to_dex = _slug_to_dex(load("pokemon.json") or [])
    sections = ""
    for rank in ["Gym Leader", "Elite Four", "Champion", "Trainer"]:
        group = [t for t in rows if t["rank"] == rank]
        if not group:
            continue
        rank_class = "rank-pill rank-champion" if rank == "Champion" else "rank-pill"
        cards = "".join(_trainer_card_html(t, slug_to_dex, rank_class) for t in group)
        label = rank + ("s" if rank != "Elite Four" else "")
        sections += f'<h2>{label} <span class="badge">{len(group)}</span></h2>{cards}'
    content = f"""
    <div class="callout"><strong>Auto-generated</strong> from <code>rctmod/trainers</code> —
    real rosters, straight from the datapack. Sprites link into the <a href="../pokemon/index.html">Pokédex</a>.</div>
    {sections}
    """
    write_page(f"gameplay/trainers/{region.lower()}.html", f"{region} Trainers", content,
        crumb=f'<a href="../../index.html">Home</a> / <a href="index.html">Trainers &amp; Gyms</a> / {region}',
        lede=f"{len(rows)} named trainers in {region}, grouped by rank.")
    print(f"  trainers/{region.lower()}.html -> {len(rows)} trainers")

def build_villains_page(trainers):
    villains = [t for t in trainers if t.get("org")]
    if not villains:
        return
    slug_to_dex = _slug_to_dex(load("pokemon.json") or [])
    by_org = {}
    for t in villains:
        by_org.setdefault(t["org"], []).append(t)
    sections = ""
    for org, rows in by_org.items():
        bosses = [t for t in rows if "Boss" in t["rank"]]
        admins = [t for t in rows if "Admin" in t["rank"]]
        grunts = [t for t in rows if "Grunt" in t["rank"]]
        cards = "".join(_trainer_card_html(t, slug_to_dex, "rank-pill rank-villain") for t in bosses + admins)
        grunt_species = sorted(set(clean_pokemon_name(p["species"]) for t in grunts for p in t["team"]))
        grunt_rows = "".join(f'<tr><td>{t["name"]}</td><td class="mono">'
                              f'{", ".join(clean_pokemon_name(p["species"]) for p in t["team"])}</td>'
                              f'<td class="mono">Lv {t["level_range"][0]}\u2013{t["level_range"][1]}</td></tr>'
                              for t in sorted(grunts, key=lambda t: t["name"]) if t.get("level_range"))
        sections += f"""
        <h2>{org} <span class="badge">{len(rows)} trainers</span></h2>
        {cards}
        <h3>{org} Grunts <span class="badge">{len(grunts)}</span></h3>
        <p>Commonly fielded: <span class="mono">{', '.join(grunt_species[:20])}{'…' if len(grunt_species) > 20 else ''}</span></p>
        <table class="grunt-table"><tr><th>Name</th><th>Team</th><th>Levels</th></tr>{grunt_rows}</table>
        """
    content = f"""
    <div class="callout"><strong>Auto-generated</strong> from <code>rctmod/trainers</code> — {len(villains)}
    villainous-team trainers across {len(by_org)} organizations.</div>
    {sections}
    """
    write_page("gameplay/trainers/villains.html", "Villainous Teams", content,
        crumb='<a href="../../index.html">Home</a> / <a href="index.html">Trainers &amp; Gyms</a> / Villainous Teams',
        lede=f"{len(villains)} trainers across {len(by_org)} organizations — bosses, admins, and grunts.")
    print(f"  trainers/villains.html -> {len(villains)} trainers across {len(by_org)} orgs")

def build_trainers_other_page(trainers):
    rows = [t for t in trainers if not t.get("org") and t["region"] not in ("Kanto", "Johto", "Hoenn", "Sinnoh", "Hisui")
            or (not t.get("org") and t["rank"] in ("Rival", "Story NPC", "LumyMon NPC", "Custom Trainer"))]
    seen = set()
    uniq = []
    for t in rows:
        if t["slug"] in seen:
            continue
        seen.add(t["slug"])
        uniq.append(t)
    if not uniq:
        return
    slug_to_dex = _slug_to_dex(load("pokemon.json") or [])
    cards = "".join(_trainer_card_html(t, slug_to_dex) for t in
                     sorted(uniq, key=lambda t: (t["region"], t["rank"], t["name"])))
    content = f"""
    <div class="callout"><strong>Auto-generated</strong> from <code>rctmod/trainers</code>.</div>
    <p>Rivals, story NPCs, LumyMon cartographer-adjacent trainers, and custom mod-exclusive characters
    that don't fit a regional gym ladder.</p>
    {cards}
    """
    write_page("gameplay/trainers/other.html", "Other Notable Trainers", content,
        crumb='<a href="../../index.html">Home</a> / <a href="index.html">Trainers &amp; Gyms</a> / Other',
        lede=f"{len(uniq)} rivals, NPCs, and one-off trainers.")
    print(f"  trainers/other.html -> {len(uniq)} trainers")

def build_trainers_pages():
    trainers = load("trainers.json")
    if not trainers:
        write_page("gameplay/trainers/index.html", "Trainers & Gyms", basic_guide_page("Trainers & Gyms"),
            crumb='<a href="../../index.html">Home</a> / Trainers & Gyms')
        print("  trainers/index.html -> placeholder (no trainers.json)")
        return
    build_trainers_index(trainers)
    for region in ["Kanto", "Johto", "Hoenn", "Sinnoh", "Hisui"]:
        build_trainers_region_page(region, trainers)
    build_villains_page(trainers)
    build_trainers_other_page(trainers)
    print(f"  trainers/index.html -> {len(trainers)} total trainers")

# =================================================================
# MEGA EVOLUTION  ->  gameplay/items/mega-evolution.html
# =================================================================
def build_mega_evolution_page():
    data = load("mega_evolutions.json")
    if not data or not data.get("stones"):
        write_page("gameplay/items/mega-evolution.html", "Mega Evolution", basic_guide_page("Mega Evolution"),
            crumb='<a href="../../index.html">Home</a> / Items / Mega Evolution')
        print("  mega-evolution.html -> placeholder (no mega_evolutions.json)")
        return

    stones = data["stones"]
    mons = load("pokemon.json") or []
    slug_to_dex = {m["slug"]: m["dex"] for m in mons if m.get("dex")}

    rows = ""
    for s in stones:
        name = clean_pokemon_name(s["species"]) if s["species"] else s["slug"].replace("_", " ").title()
        form = f' <span class="badge">{s["form"]}</span>' if s["form"] else ""
        dex = slug_to_dex.get(s["species"])
        img = (f'<img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{dex}.png" '
               f'alt="{name}" width="32" height="32" style="image-rendering:pixelated;vertical-align:middle;margin-right:6px;">'
               if dex else "")
        target = f'../pokemon/index.html?mon={s["species"]}' if s["species"] else "#"
        rows += (f'<tr><td>{img}<a href="{target}">{name}</a>{form}</td>'
                 f'<td class="mono">{s["source_item"]}</td><td class="mono">{s["result_item"]}</td></tr>')

    special_rows = "".join(
        f'<tr><td class="mono">{s["result_item"]}</td><td class="mono">{", ".join(s["ingredients"])}</td></tr>'
        for s in data.get("special_items", [])
    )

    content = f"""
    <div class="callout"><strong>Auto-generated</strong> from <code>zamegas/recipe</code> and
    <code>mega_showdown/recipe</code>. Species matched against this pack's own Pokédex data by name
    similarity — double-check any you're unsure of in-game.</div>
    <h2>What is it?</h2>
    <p>CobbleVerse adds Mega Evolution via the <strong>Mega Showdown</strong> mod, and goes well beyond the
    official Mega roster — Pokémon that never had a canon Mega form (Meganium, Greninja, Feraligatr, Emboar,
    Zeraora, Raichu, and more) get custom Mega Stones here, alongside official ones.</p>
    <h2>Where do I find the base stones?</h2>
    <div class="fill">Each recipe converts a raw <code>lumymon:</code> stone into the usable
    <code>zamega:</code> item — but the datapacks don't say where the raw stone drops. Likely a raid reward
    for that Pokémon's Mega raid boss (see the Raids page) — confirm in-game and fill in here.</div>
    <h2>Mega Stones <span class="badge">{len(stones)}</span></h2>
    <table><tr><th>Pokémon</th><th>Crafted From</th><th>Result Item</th></tr>{rows}</table>
    <h2>Special Evolution Items</h2>
    <p>A few extra crafting recipes bundled with the Mega Showdown mod itself (Zygarde assembly, Ash-Greninja,
    and a couple of unclear catalyst items — worth checking in-game what these actually unlock):</p>
    <table><tr><th>Result</th><th>Ingredients</th></tr>{special_rows}</table>
    <h2>Related Pages</h2>
    <p>Several Mega Evolutions also appear as <a href="../mechanics/raids.html">Raid bosses</a> —
    check the raid tiers for the ones encounterable that way.</p>
    <h2>Tips &amp; Strategies</h2>
    <ul class="tasks"><li>{fill("How to actually trigger a Mega Evolution in battle on this server")}</li>
    <li>{fill("Any restrictions — one Mega per team, format legality, etc.")}</li></ul>
    """
    write_page("gameplay/items/mega-evolution.html", "Mega Evolution", content,
        crumb='<a href="../../index.html">Home</a> / Items / Mega Evolution',
        lede=f"{len(stones)} custom Mega Stones craftable on this server, pulled from the Mega Showdown datapacks.")
    print(f"  mega-evolution.html -> {len(stones)} mega stones")

# =================================================================
# SEARCH INDEX  ->  assets/data/search-index.json
# =================================================================
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
_H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
_CRUMB_RE = re.compile(r'<div class="crumb">(.*?)</div>', re.S)
_MAIN_RE = re.compile(r"<main>(.*?)</main>", re.S)

def _text_of(fragment):
    return _WS_RE.sub(" ", html_lib.unescape(_TAG_RE.sub(" ", fragment))).strip()

def _page_search_fields(page_html):
    m = _MAIN_RE.search(page_html)
    if not m:
        return None
    main_html = m.group(1)
    h1m = _H1_RE.search(main_html)
    title = _text_of(h1m.group(1)) if h1m else ""
    crumbm = _CRUMB_RE.search(main_html)
    section = _text_of(crumbm.group(1)) if crumbm else ""
    body = main_html
    if h1m:
        body = body.replace(h1m.group(0), " ")
    if crumbm:
        body = body.replace(crumbm.group(0), " ")
    text = _text_of(body)[:1200]
    return title, section, text

REGION_FILE = {"Kanto": "kanto", "Johto": "johto", "Hoenn": "hoenn", "Sinnoh": "sinnoh", "Hisui": "hisui"}

def build_search_index():
    entries = []
    for f in glob.glob(os.path.join(SITE_ROOT, "**", "*.html"), recursive=True):
        rel_path = os.path.relpath(f, SITE_ROOT).replace(os.sep, "/")
        with open(f, "r", encoding="utf-8") as fh:
            page_html = fh.read()
        fields = _page_search_fields(page_html)
        if not fields:
            continue
        title, section, text = fields
        if not title:
            continue
        entries.append({"type": "page", "title": title, "url": rel_path, "section": section, "text": text})

    mons = load("pokemon.json") or []
    for m in mons:
        biomes = sorted({b for s in m.get("spawns", []) for b in s.get("biomes", [])})
        bits = [f"#{m['dex']:04d}", m.get("best_bucket") or ""]
        if biomes:
            bits.append(", ".join(biomes[:6]))
        entries.append({
            "type": "pokemon", "title": m["name"],
            "url": f"gameplay/pokemon/index.html?mon={m['slug']}",
            "section": "Pokédex", "text": " · ".join(b for b in bits if b),
        })

    trainers = load("trainers.json") or []
    trainer_count = 0
    for t in trainers:
        if "Grunt" in t["rank"]:
            continue  # too many, too low-value individually — the org page text still covers them
        if t.get("org"):
            url = "gameplay/trainers/villains.html"
        else:
            region_file = REGION_FILE.get(t["region"])
            url = f"gameplay/trainers/{region_file}.html" if region_file else "gameplay/trainers/other.html"
        url += f"#trainer-{t['slug']}"
        species = ", ".join(clean_pokemon_name(p["species"]) for p in t["team"][:6])
        entries.append({
            "type": "trainer", "title": t["name"],
            "url": url, "section": "Trainers & Gyms",
            "text": f"{t['rank']} · {t['region']} · Team: {species}",
        })
        trainer_count += 1

    items = load("items.json") or []
    for it in items:
        entries.append({
            "type": "item", "title": it["name"],
            "url": f"gameplay/items/database.html?q={it['name'].replace(' ', '+')}",
            "section": it["category"],
            "text": it.get("desc", ""),
        })

    out_dir = os.path.join(SITE_ROOT, "assets", "data")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "search-index.json"), "w", encoding="utf-8") as f:
        json.dump(entries, f, separators=(",", ":"), ensure_ascii=False)
    page_count = sum(1 for e in entries if e["type"] == "page")
    print(f"  search-index.json -> {len(entries)} entries ({page_count} pages, {len(mons)} Pokémon, {trainer_count} trainers, {len(items)} items)")

# =================================================================
# ITEM DATABASE  ->  gameplay/items/database.html
# =================================================================
def build_items_database_page():
    items = load("items.json")
    if not items:
        write_page("gameplay/items/database.html", "Item Database", basic_guide_page("Item Database"),
            crumb='<a href="../../index.html">Home</a> / Items / Item Database')
        print("  items/database.html -> placeholder (no items.json)")
        return

    data_dir = os.path.join(SITE_ROOT, "assets", "data")
    os.makedirs(data_dir, exist_ok=True)
    with open(os.path.join(data_dir, "items.json"), "w", encoding="utf-8") as f:
        json.dump(items, f, separators=(",", ":"), ensure_ascii=False)

    cat_counts = {}
    for it in items:
        cat_counts[it["category"]] = cat_counts.get(it["category"], 0) + 1
    cat_summary = " · ".join(f"{v} {k}" for k, v in sorted(cat_counts.items(), key=lambda kv: -kv[1]))

    content = f"""
    <div class="callout"><strong>{len(items)} items</strong>, scraped from the official
    <a href="https://wiki.cobblemon.com/index.php?title=Category:Item" target="_blank" rel="noopener">Cobblemon Wiki's item category</a>
    and organized using its own category structure. Summaries are written fresh for this wiki, not copied —
    click through to the official page on any card for full detail, crafting recipes, and images.</div>
    <p class="mono" style="font-size:.75rem;">{cat_summary}</p>

    <div data-items-root data-items-json="../../assets/data/items.json">
      <div class="dex-toolbar">
        <input class="dex-search" type="search" placeholder="Search items by name or effect…" aria-label="Search items">
        <span class="dex-count"></span>
        <div class="dex-chip-row categories" aria-label="Filter by category"></div>
      </div>
      <div class="dex-grid items-grid"><div class="dex-empty">Loading items…</div></div>
    </div>

    <p class="mono" style="font-size:.7rem;">A handful of very recently added items may not be listed yet —
    the <a href="https://wiki.cobblemon.com/index.php?title=Category:Item" target="_blank" rel="noopener">official category page</a>
    is always the complete, current source.</p>
    """
    write_page("gameplay/items/database.html", "Item Database", content,
        crumb='<a href="../../index.html">Home</a> / Items / Item Database',
        lede=f"{len(items)} items across {len(cat_counts)} categories — search, filter, click through for full detail.")

    path = os.path.join(SITE_ROOT, "gameplay/items/database.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    html = html.replace("</body>", f'<script src="../../assets/js/items.js?v={BUILD_STAMP}"></script>\n</body>')
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  items/database.html -> {len(items)} items across {len(cat_counts)} categories")

# =================================================================
def main():
    print("Building data-driven pages...")
    build_raids_page()
    build_structures_page()
    build_legendary_monuments_page()
    build_biomes_page()
    build_tms_page()
    build_fossils_page()
    build_lumymon_page()
    build_pokedex_page()
    build_trainers_pages()
    build_mega_evolution_page()
    build_items_database_page()
    build_search_index()  # must run last — it scans the final rendered HTML of every page
    print("\nDone. These pages now reflect the extracted datapack data:")
    print("  gameplay/mechanics/raids.html")
    print("  gameplay/world/legendary-monuments.html")
    print("  gameplay/items/tms.html")
    print("  gameplay/items/fossils.html")
    print("  gameplay/server-features/lumymon.html")
    print("  gameplay/pokemon/index.html  (Pokédex app)")
    print("  gameplay/trainers/*.html     (Trainers & Gyms)")
    print("  gameplay/items/mega-evolution.html")
    print("  assets/data/search-index.json (site-wide search)")

if __name__ == "__main__":
    main()
