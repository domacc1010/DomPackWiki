#!/usr/bin/env python3
"""
extract_data.py — pulls structured data out of the CobbleVerse datapacks
and writes it to tools/data/*.json. Re-run this any time the datapacks are
updated, then run build_site.py to refresh the affected wiki pages.

Usage:
    python3 tools/extract_data.py /path/to/unzipped/datapacks

The path should point at the folder that directly contains things like
COBBLEVERSE-DP-v19-CF/, COBBLEVERSE-Loot-DP-v11/, extra/, etc. — i.e. the
"datapacks" folder from inside datapacks.zip.

What it extracts (see the README in this folder for the full list):
  - raid_bosses.json     <- cobblemonraiddens/raid/boss/*.json
  - raid_modifiers.json  <- cobblemonraiddens/raid/boss_additions/*.json
  - legendary_sites.json <- extra/*/data/cobbleverse/worldgen/structure/{legendary,mythical}/*.json
                            + matching worldgen/structure_set/ entries for spacing/rarity
  - tm_recipes.json      <- data/tmcraft/recipe/*.json
  - fossils.json         <- data/cobblemon/fossils/*.json
  - lumymon_maps.json    <- data/lumymon/trades/*_cartographer.json (treasure map trades)

Every extractor is defensive: if a datapack is missing or a folder doesn't
exist, that section just comes back empty instead of crashing, since mod
packs get added/removed between server updates.
"""
import json, os, re, sys, glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from site_common import clean_pokemon_name  # noqa: E402

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def find(root, *parts, ext=".json"):
    """Glob-find files under root/**/parts-joined/**/*.ext"""
    pattern = os.path.join(root, "**", *parts, "**", f"*{ext}")
    return sorted(glob.glob(pattern, recursive=True))

MC_COLOR_CODES = re.compile(r"§.")

def clean_name(s):
    if not s:
        return s
    return MC_COLOR_CODES.sub("", s).strip()

# ---------------------------------------------------------------
# 1. Raid bosses + modifiers
# ---------------------------------------------------------------
def extract_raids(root):
    bosses = []
    for f in find(root, "cobblemonraiddens", "raid", "boss"):
        if "boss_additions" in f:
            continue
        try:
            d = load_json(f)
        except Exception:
            continue
        pokemon = d.get("pokemon", {})
        bosses.append({
            "slug": os.path.splitext(os.path.basename(f))[0],
            "species": pokemon.get("species"),
            "moves": pokemon.get("moves", []),
            "custom_properties": pokemon.get("custom_properties", []),
            "tier": d.get("raid_tier"),
            "type": d.get("raid_type"),
            "weight": d.get("weight"),
        })

    modifiers = []
    for f in find(root, "cobblemonraiddens", "raid", "boss_additions"):
        try:
            d = load_json(f)
        except Exception:
            continue
        modifiers.append({
            "slug": os.path.splitext(os.path.basename(f))[0],
            "feature": d.get("additions", {}).get("raid_feature"),
            "type": d.get("additions", {}).get("raid_type"),
            "weight": d.get("additions", {}).get("weight"),
        })

    return {"bosses": bosses, "modifiers": modifiers}

# ---------------------------------------------------------------
# 2. Legendary / mythical world spawn sites (structure + structure_set)
# ---------------------------------------------------------------
REGION_DIR_MAP = {
    "COBBLEVERSE-Hoenn-DP": "Hoenn",
    "COBBLEVERSE-Sinnoh-DP": "Sinnoh",
    "COBBLEVERSE-Johto-DP": "Johto",
}

def infer_dimension(biome):
    if not biome:
        return "Overworld"
    b = biome.lower()
    if "end" in b:
        return "The End"
    if "nether" in b or "basalt" in b or "soul_sand" in b:
        return "Nether"
    return "Overworld"

def extract_legendary_sites(root):
    sites = []
    for region_dir, region_name in REGION_DIR_MAP.items():
        base = os.path.join(root, "extra", region_dir, "data", "cobbleverse", "worldgen")
        struct_dir = os.path.join(base, "structure")
        set_dir = os.path.join(base, "structure_set")
        for category in ("legendary", "mythical"):
            cat_dir = os.path.join(struct_dir, category)
            if not os.path.isdir(cat_dir):
                continue
            for f in sorted(glob.glob(os.path.join(cat_dir, "*.json"))):
                name = os.path.splitext(os.path.basename(f))[0]
                try:
                    sd = load_json(f)
                except Exception:
                    continue
                set_path = os.path.join(set_dir, category, os.path.basename(f))
                spacing = separation = None
                if os.path.isfile(set_path):
                    try:
                        setd = load_json(set_path)
                        placement = setd.get("placement", {})
                        spacing = placement.get("spacing")
                        separation = placement.get("separation")
                    except Exception:
                        pass
                biome = sd.get("biomes")
                sites.append({
                    "name": name,
                    "region": region_name,
                    "category": category,
                    "biome": biome if isinstance(biome, str) else biome,
                    "dimension": infer_dimension(biome if isinstance(biome, str) else str(biome)),
                    "start_height": sd.get("start_height"),
                    "spacing": spacing,
                    "separation": separation,
                })
    return sites

# ---------------------------------------------------------------
# 3. TM crafting recipes
# ---------------------------------------------------------------
DISC_TIER_ORDER = ["copper_blank_disc", "iron_blank_disc", "gold_blank_disc", "emerald_blank_disc",
                    "diamond_blank_disc", "netherite_blank_disc"]

def extract_tm_recipes(root):
    recipes = []
    for f in find(root, "tmcraft", "recipe"):
        try:
            d = load_json(f)
        except Exception:
            continue
        result_id = d.get("result", {}).get("id", "")
        move = result_id.replace("tmcraft:tm_", "")
        ingredients = [v.get("item") for v in d.get("key", {}).values() if v.get("item")]
        disc = next((i for i in ingredients if i and "blank_disc" in i), None)
        others = [i for i in ingredients if i != disc]
        recipes.append({
            "move": move,
            "result_id": result_id,
            "disc": disc.replace("tmcraft:", "") if disc else None,
            "ingredients": [i for i in others],
        })
    recipes.sort(key=lambda r: (DISC_TIER_ORDER.index(r["disc"]) if r["disc"] in DISC_TIER_ORDER else 99, r["move"]))
    return recipes

# ---------------------------------------------------------------
# 4. Fossils
# ---------------------------------------------------------------
def extract_fossils(root):
    fossils = []
    for f in find(root, "cobblemon", "fossils"):
        try:
            d = load_json(f)
        except Exception:
            continue
        fossils.append({
            "result": d.get("result"),
            "fossils": d.get("fossils", []),
            "slug": os.path.splitext(os.path.basename(f))[0],
        })
    return fossils

# ---------------------------------------------------------------
# 5. LumyMon cartographer treasure-map trades
# ---------------------------------------------------------------
def extract_lumymon_maps(root):
    npcs = []
    for f in find(root, "lumymon", "trades"):
        base = os.path.splitext(os.path.basename(f))[0]  # e.g. johto_cartographer
        if "cartographer" not in base:
            continue
        try:
            d = load_json(f)
        except Exception:
            continue
        region = base.split("_")[0].title()
        trades = []
        for tier in d.get("tiers", []):
            for group in tier.get("groups", []):
                for t in group.get("trades", []):
                    cost_a = t.get("cost_a", {}).get("name")
                    dest = display = None
                    for fn in t.get("result", {}).get("functions", []):
                        if fn.get("function") == "minecraft:exploration_map":
                            dest = fn.get("destination")
                        if fn.get("function") == "minecraft:set_name":
                            display = clean_name(fn.get("name"))
                    trades.append({"tome": cost_a, "destination": dest, "display_name": display})
        npcs.append({"npc": base, "region": region, "trades": trades})
    return npcs

# ---------------------------------------------------------------
# 6. Pokémon spawn data (every species in cobblemon/spawn_pool_world)
# ---------------------------------------------------------------
def clean_biome(tag):
    if not tag:
        return tag
    t = tag.lstrip("#")
    t = t.split(":")[-1]
    if t.startswith("is_"):
        t = t[3:]
    return t.replace("_", " ").title()

BUCKET_ORDER = ["common", "uncommon", "rare", "ultra-rare"]

def extract_pokemon(root):
    mons = []
    spawn_dir_glob = os.path.join(root, "**", "cobblemon", "spawn_pool_world", "*.json")
    for f in sorted(glob.glob(spawn_dir_glob, recursive=True)):
        base = os.path.splitext(os.path.basename(f))[0]  # e.g. "0001_bulbasaur"
        parts = base.split("_", 1)
        dex_num = int(parts[0]) if parts[0].isdigit() else None
        slug = parts[1] if len(parts) > 1 else base
        try:
            d = load_json(f)
        except Exception:
            continue
        if not d.get("enabled", True):
            continue
        spawns_raw = d.get("spawns", [])
        if not spawns_raw:
            continue
        display_name = clean_pokemon_name(slug)
        spawns_out = []
        buckets_seen = set()
        for s in spawns_raw:
            cond = s.get("condition", {}) or {}
            anticond = s.get("anticondition", {}) or {}
            level = s.get("level", "")
            lvl_min = lvl_max = None
            if isinstance(level, str) and "-" in level:
                try:
                    lo, hi = level.split("-")
                    lvl_min, lvl_max = int(lo), int(hi)
                except Exception:
                    pass
            elif isinstance(level, (int, str)) and str(level).isdigit():
                lvl_min = lvl_max = int(level)
            bucket = s.get("bucket")
            if bucket:
                buckets_seen.add(bucket)
            biomes = [clean_biome(b) for b in cond.get("biomes", [])]
            anti_biomes = [clean_biome(b) for b in anticond.get("biomes", [])]
            time = cond.get("timeRange")
            weather = "rain" if cond.get("isRaining") else ("thunder" if cond.get("isThundering") else None)
            spawns_out.append({
                "bucket": bucket,
                "position": s.get("spawnablePositionType"),
                "presets": s.get("presets", []),
                "level_min": lvl_min, "level_max": lvl_max,
                "weight": s.get("weight"),
                "biomes": biomes,
                "anti_biomes": anti_biomes,
                "time": time,
                "weather": weather,
                "min_sky_light": cond.get("minSkyLight"),
                "max_sky_light": cond.get("maxSkyLight"),
                "can_see_sky": cond.get("canSeeSky"),
                "min_y": cond.get("minY"), "max_y": cond.get("maxY"),
                "structures": cond.get("structures", []),
                "moon_phase": cond.get("moonPhase", []),
                "slime_chunk": cond.get("isSlimeChunk"),
                "min_lure_level": cond.get("minLureLevel"),
                "rod_type": cond.get("rodType"),
                "bait": cond.get("bait"),
            })
        best_bucket = None
        for b in BUCKET_ORDER:
            if b in buckets_seen:
                best_bucket = b
                break
        mons.append({
            "dex": dex_num,
            "slug": slug,
            "name": display_name,
            "best_bucket": best_bucket,
            "buckets": sorted(buckets_seen, key=lambda b: BUCKET_ORDER.index(b) if b in BUCKET_ORDER else 99),
            "spawns": spawns_out,
        })
    mons.sort(key=lambda m: (m["dex"] is None, m["dex"]))
    return mons

# ---------------------------------------------------------------
# 7. Custom species overrides (full stat-block Pokémon tuned by this pack)
# ---------------------------------------------------------------
def extract_species_overrides(root):
    out = []
    for f in find(root, "cobblemon", "species"):
        if "species_additions" in f or "species_features" in f or "species_feature_assignments" in f:
            continue
        try:
            d = load_json(f)
        except Exception:
            continue
        out.append({
            "slug": os.path.splitext(os.path.basename(f))[0],
            "name": d.get("name"),
            "dex": d.get("nationalPokedexNumber"),
            "primary_type": d.get("primaryType"),
            "secondary_type": d.get("secondaryType"),
            "abilities": d.get("abilities", []),
            "base_stats": d.get("baseStats", {}),
            "height": d.get("height"),
            "weight": d.get("weight"),
            "catch_rate": d.get("catchRate"),
            "egg_groups": d.get("eggGroups", []),
            "labels": d.get("labels", []),
        })
    return out

# ---------------------------------------------------------------
# 8. Trainers, Gym Leaders, Elite Four, Champions, Rivals, Villain Teams
# ---------------------------------------------------------------
REGION_LABELS = {
    "kanto": "Kanto", "johto": "Johto", "hoenn": "Hoenn", "sinnoh": "Sinnoh",
    "hisui": "Hisui", "galaxy": "Hisui", "lumy": "LumyMon", "mod": "Custom",
    "pallet": "Kanto", "rival": "Kanto", "old": "Kanto",
}
ORG_LABELS = {
    "team_rocket": "Team Rocket", "team_galactic": "Team Galactic",
    "team_aqua": "Team Aqua", "team_magma": "Team Magma",
}
BOSS_NAMES = {"giovanni", "cyrus"}
ADMIN_KEYWORDS = ("commander", "admin", "general", "director", "supervisor", "charon")

def classify_trainer(slug):
    """Returns (region, rank, org) from a trainers/*.json filename slug."""
    parts = slug.split("_")
    head = parts[0]

    if head == "team":
        org_key = "_".join(parts[:2])
        org = ORG_LABELS.get(org_key, org_key.replace("_", " ").title())
        rest = "_".join(parts[2:])
        region = {"team_rocket": "Kanto", "team_galactic": "Sinnoh",
                   "team_aqua": "Hoenn", "team_magma": "Hoenn"}.get(org_key, "")
        if any(b in rest for b in BOSS_NAMES):
            rank = f"{org} Boss"
        elif any(k in rest for k in ADMIN_KEYWORDS):
            rank = f"{org} Admin"
        else:
            rank = f"{org} Grunt"
        return region, rank, org

    region = REGION_LABELS.get(head, head.title())

    if head in ("pallet", "rival", "old", "lumy", "mod"):
        rank = {"pallet": "Story NPC", "rival": "Rival", "old": "Story NPC",
                "lumy": "LumyMon NPC", "mod": "Custom Trainer"}[head]
        return region, rank, None

    if head in ("galaxy",):
        return region, "Trainer", None

    if "champion" in parts:
        return region, "Champion", None
    if "league" in parts:
        return region, "Elite Four", None
    if head == "hisui":
        return region, "Trainer", None
    return region, "Gym Leader", None

def extract_trainers(root):
    trainer_dir = None
    for f in find(root, "rctmod", "trainers", ext=".json"):
        if os.sep + "trainers" + os.sep in f and "mobs" not in f and "trainer_types" not in f:
            trainer_dir = os.path.dirname(f)
            break
    if not trainer_dir:
        return []

    mobs_single_dir = os.path.join(os.path.dirname(trainer_dir), "mobs", "trainers", "single")

    trainers = []
    for fpath in sorted(glob.glob(os.path.join(trainer_dir, "*.json"))):
        slug = os.path.splitext(os.path.basename(fpath))[0]
        try:
            d = load_json(fpath)
        except Exception:
            continue
        name = clean_name(d.get("name", {}).get("literal")) or slug.split("_")[-1].title()
        name = name.replace("_", " ")
        region, rank, org = classify_trainer(slug)

        team = []
        for p in d.get("team", []):
            team.append({
                "species": p.get("species"),
                "level": p.get("level"),
                "gender": p.get("gender"),
                "nature": p.get("nature"),
                "ability": p.get("ability"),
                "moveset": p.get("moveset", []),
                "held_item": p.get("heldItem", []),
                "ivs": p.get("ivs", {}),
                "evs": p.get("evs", {}),
            })

        biomes = []
        mob_path = os.path.join(mobs_single_dir, slug + ".json")
        if os.path.isfile(mob_path):
            try:
                md = load_json(mob_path)
                biomes = [clean_biome(b) for b in md.get("biomeTagWhitelist", [])]
            except Exception:
                pass

        levels = [p["level"] for p in team if p.get("level")]
        trainers.append({
            "slug": slug,
            "name": name,
            "region": region,
            "rank": rank,
            "org": org,
            "battle_format": d.get("battleFormat"),
            "bag": [{"item": (b.get("item") or "").replace("cobblemon:", "").replace("_", " "),
                     "quantity": b.get("quantity")} for b in d.get("bag", [])],
            "team": team,
            "team_count": len(team),
            "level_range": [min(levels), max(levels)] if levels else None,
            "biomes": biomes,
        })
    return trainers

# ---------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python3 extract_data.py /path/to/datapacks")
        sys.exit(1)
    root = sys.argv[1]
    if not os.path.isdir(root):
        print(f"Not a directory: {root}")
        sys.exit(1)

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(out_dir, exist_ok=True)

    datasets = {
        "raids.json": extract_raids(root),
        "legendary_sites.json": extract_legendary_sites(root),
        "tm_recipes.json": extract_tm_recipes(root),
        "fossils.json": extract_fossils(root),
        "lumymon_maps.json": extract_lumymon_maps(root),
        "pokemon.json": extract_pokemon(root),
        "species_overrides.json": extract_species_overrides(root),
        "trainers.json": extract_trainers(root),
    }

    for filename, data in datasets.items():
        out_path = os.path.join(out_dir, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        count = len(data) if isinstance(data, list) else sum(len(v) for v in data.values())
        print(f"  wrote {filename}  ({count} entries)")

    print("\nDone. Now run: python3 tools/build_site.py")

if __name__ == "__main__":
    main()
