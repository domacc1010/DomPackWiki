#!/usr/bin/env python3
"""
build_static_pages.py — regenerates every template/placeholder page on the
site (home, getting-started, mechanics, world, server-features, decorations,
progression guide, FAQ, rules, technical, mod list, sources) using the
current NAV in site_common.py.

Run this FIRST whenever NAV changes in site_common.py (e.g. after adding a
new section), so every page's sidebar stays in sync — then run
build_dynamic_pages.py to lay the real datapack-driven content back on top
of the 5 pages it owns.

Pages this script does NOT touch: gameplay/pokemon/index.html — that one is
owned by build_dynamic_pages.py (auto-generated Pokédex app). Everything
else, including gameplay/items/index.html, is regenerated here every run so
its sidebar never drifts out of sync with the NAV in site_common.py.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from site_common import write_page, fill, basic_guide_page, server_feature_page  # noqa: E402

# ---------------------------------------------------------------
# HOME
# ---------------------------------------------------------------
def build_home():
    content = """
    <div class="card-grid">
      <div class="card bevel"><h3>Getting Started</h3><p>New player onboarding — starter, controls, commands, first Pokémon, waystones.</p></div>
      <div class="card bevel"><h3>Pokémon</h3><p>The largest section. Types, spawns, moves, breeding, competitive builds.</p></div>
      <div class="card bevel"><h3>Server Features</h3><p>CobbleDollars, Badges, Legendary Monuments — systems unique to this server.</p></div>
      <div class="card bevel"><h3>Technical</h3><p>Admin commands, configs, performance mods, troubleshooting.</p></div>
    </div>
    <h2>Server Systems</h2>
    <ul class="tasks">
      <li>CobbleDollars</li><li>Badges</li><li>Legendary Monuments</li>
      <li>Safe Pastures</li><li>Economy</li><li>Custom Features</li>
    </ul>
    <div class="callout"><strong>Build order tip:</strong> Write Server Features first (no source exists anywhere
    else for those), then Getting Started (short, high traffic), then batch-generate Pokémon pages last from the
    Cobblemon datapacks — see the Sources page.</div>
    """
    write_page("index.html", "CobbleVerse Wiki", content, crumb="Home",
        lede="The official guide for CobbleVerse — a DomPack player guide, not a pasted-together mod list.")

# ---------------------------------------------------------------
GS_PAGES = [
    ("starter-guide", "Starter Guide"), ("controls", "Controls"), ("commands", "Commands"),
    ("first-pokemon", "First Pokémon"), ("money", "Money (CobbleDollars)"), ("badges", "Badges"),
    ("waystones", "Waystones"), ("breeding", "Breeding"), ("raids", "Raids"),
]
def build_getting_started():
    for slug, title in GS_PAGES:
        write_page(f"gameplay/getting-started/{slug}.html", title, basic_guide_page(title),
            crumb=f'<a href="../../index.html">Home</a> / Getting Started / {title}')

# ---------------------------------------------------------------
MECH_PAGES = [
    ("battle-system", "Battle System"), ("status-conditions", "Status Conditions"), ("weather", "Weather"),
    ("day-night", "Day/Night Cycle"), ("friendship", "Friendship"), ("breeding", "Breeding"),
    ("pastures", "Pastures"), ("ride-pokemon", "Ride Pokémon"), ("following-pokemon", "Following Pokémon"),
    ("shiny-pokemon", "Shiny Pokémon"), ("legendary-spawning", "Legendary Spawning"),
    ("fishing", "Fishing"), ("cooking", "Cooking"),
    # NOTE: "raids" deliberately excluded — owned by build_dynamic_pages.py
]
def build_mechanics():
    for slug, title in MECH_PAGES:
        write_page(f"gameplay/mechanics/{slug}.html", title, basic_guide_page(title),
            crumb=f'<a href="../../index.html">Home</a> / Mechanics / {title}')

# ---------------------------------------------------------------
WORLD_PAGES = [
    ("villages", "Villages"),
    ("waystones", "Waystones"), ("nether", "Nether"), ("the-end", "The End"), ("custom-builds", "Custom Builds"),
    # NOTE: "biomes", "structures", and "legendary-monuments" deliberately excluded — owned by build_dynamic_pages.py
]
def build_world():
    for slug, title in WORLD_PAGES:
        write_page(f"gameplay/world/{slug}.html", title, basic_guide_page(title),
            crumb=f'<a href="../../index.html">Home</a> / World / {title}')

# ---------------------------------------------------------------
SF_PAGES = [
    ("cobbledollars", "CobbleDollars"), ("badges", "CobbleVerse Badges"),
    ("legendary-monuments", "Legendary Monuments"), ("safe-pastures", "Safe Pastures"),
    ("cobblecuisine", "CobbleCuisine"), ("cobblefurnies", "CobbleFurnies"), ("economy", "Economy Overview"),
    # NOTE: "lumymon" deliberately excluded — owned by build_dynamic_pages.py
]
def build_server_features():
    for slug, title in SF_PAGES:
        write_page(f"gameplay/server-features/{slug}.html", title, server_feature_page(),
            crumb=f'<a href="../../index.html">Home</a> / Server Features / {title}')

# ---------------------------------------------------------------
def build_items_index():
    content = """
    <p>One page per item, or group small/similar items into a single page per category (recommended for
    anything with dozens of near-identical entries, like TMs).</p>
    <h2>Auto-Generated Item Pages</h2>
    <div class="card-grid">
      <div class="card bevel"><h3><a href="tms.html">TM Crafting</a></h3><p>Every craftable TM recipe, pulled from the datapacks.</p></div>
      <div class="card bevel"><h3><a href="fossils.html">Fossils</a></h3><p>Fossil restoration combinations, pulled from the datapacks.</p></div>
      <div class="card bevel"><h3><a href="mega-evolution.html">Mega Evolution</a></h3><p>Custom Mega Stones craftable on this server, pulled from the datapacks.</p></div>
    </div>
    <h2>Categories Still To Cover</h2>
    <ul class="tasks">
      <li>Pokéballs</li><li>Medicine</li><li>Evolution Stones</li><li>Held Items</li>
      <li>Battle Items</li><li>Food</li>
      <li>Decorative Blocks</li><li>Custom Items</li><li>Bottle Caps</li>
    </ul>
    <h2>Page Template</h2>
    <div class="bevel card">
    <h3>{Item Name}<span class="badge">TEMPLATE</span></h3>
    <h4>What is it?</h4>""" + fill("2-3 sentences") + """
    <h4>Where do I find it?</h4>""" + fill("Crafted / found / purchased") + """
    <h4>How do I use it?</h4>""" + fill("Usage instructions") + """
    <h4>Why should I care?</h4>""" + fill("Payoff / value") + """
    <h4>Tips &amp; Strategies</h4>""" + fill("Practical tips") + """
    </div>
    """
    write_page("gameplay/items/index.html", "Items", content, crumb='<a href="../../index.html">Home</a> / Items')

# ---------------------------------------------------------------
BLOCK_GROUPS = [
    ("Wood & Plants", [
        ("Apricorn Wood Set", "Log/plank/leaves set from Apricorn trees — the source of Apricorns, which craft every base Poké Ball type."),
        ("Apricorn Leaves / Sprout", "Grows Apricorns over time; five colors correspond to five base ball types."),
        ("Saccharine Wood Set", "A second custom wood set — Saccharine trees, the source of Saccharine Sap used in several recipes."),
    ]),
    ("Crops & Berries", [
        ("Berry Tree", "Grows any Berry species — used in cooking, held-item strategies, and status-cure items."),
        ("Medicinal Leek", "Crop used in several medicine recipes."),
        ("Revival Herb", "Fully heals HP and status but lowers friendship — same trade-off as the mainline games."),
        ("Vivichoke", "Cooking crop; also a common Fossil Dig Site drop."),
        ("Big Root", "Boosts HP-draining move recovery when held."),
        ("Nature Mints", "Changes a Pokémon's effective nature for battle without breeding for it."),
        ("Hearty Grains / Hearty Grain Bale", "Farmable feed crop."),
        ("Galarica Nuts", "Crafts Galarica Cuffs/Wreaths — used for Alolan/Galarian form items."),
    ]),
    ("Minerals", [
        ("Evolution Stone Ore", "Ore variant that drops raw Evolution Stones (Fire/Water/Thunder/Leaf/Moon/Sun/Shiny/Dusk/Ice/Dawn)."),
        ("Tumblestone", "Base + Sky/Black variants — crafts into Tumblestone blocks, tied to Rockruff/Alolan evolution lines."),
    ]),
    ("Utility", [
        ("PC", "Access the Pokémon storage system."),
        ("Healing Machine", "Fully heals a party — the block form of Pokémon Centers."),
        ("Pasture Block", "Lets a Pokémon roam outside its Poké Ball in a fenced area."),
        ("Campfire Pot", "Cooks Poké Snacks/Poké Cake, added in Cobblemon 1.7 ('Set Course!')."),
        ("Poké Snack / Poké Cake", "Food items that can attract wild Pokémon when placed."),
        ("Data Monitor", "Multiblock computer terminal used by several other machines."),
        ("Resurrection Machine (Fossil Analyzer / Restoration Tank)", "Restores a Pokémon from a Fossil — see this wiki's Fossils page for CobbleVerse's actual combinations."),
    ]),
    ("Decorative", [
        ("Relic Coin / Relic Coin Pouch/Sack", "Currency and storage tied to Gimmighoul."),
        ("Evolution Stone Blocks", "Decorative full-block form of each Evolution Stone."),
        ("Tatami Block Set", "Japanese-styled flooring set."),
        ("Gilded Chest / Gimmighoul Chest", "Special storage found in Ruins structures."),
        ("Display Case", "Shows off a held item or Poké Ball on a shelf."),
        ("Plaque", "Wall-mounted trophy/achievement display."),
    ]),
]

def build_blocks_page():
    sections = ""
    for group, blocks in BLOCK_GROUPS:
        rows = "".join(f"<tr><td>{name}</td><td>{desc}</td></tr>" for name, desc in blocks)
        sections += f'<h2>{group}</h2><table><tr><th>Block</th><th>What it does</th></tr>{rows}</table>'
    content = f"""
    <div class="callout"><strong>Reference content</strong> — sourced from the
    <a href="https://wiki.cobblemon.com/index.php/Category:Block">official Cobblemon Wiki's Block category</a>.
    These are base Cobblemon blocks compiled into the mod itself, not something the server's datapacks configure,
    so this page won't auto-update — edit it by hand if a future Cobblemon version adds/changes blocks.</div>
    <p>Every block Cobblemon adds, grouped the same way the official wiki groups them. This covers what each
    block <em>is</em> — for where things actually generate on this server, see
    <a href="structures.html">Structures</a> and <a href="biomes.html">Biomes</a>.</p>
    {sections}
    <h2>Related Pages</h2>
    <p><a href="structures.html">Structures</a> · <a href="../items/fossils.html">Fossils</a> ·
    <a href="../items/index.html">Items</a></p>
    """
    write_page("gameplay/world/blocks.html", "Blocks", content,
        crumb='<a href="../../index.html">Home</a> / World / Blocks',
        lede="Every block Cobblemon adds to the game, grouped by category.")

# ---------------------------------------------------------------
def build_decorations():
    content = """
    <p>Building/decor mods. Best done as one page per mod, with a block gallery inside — highly visual pages,
    so plan on screenshots in <code>/assets</code>.</p>
    <h2>Mods to Cover</h2>
    <ul class="tasks"><li>Beautify</li><li>Handcrafted</li><li>Rechiseled</li><li>Moar Concrete</li>
    <li>Carved Wood</li><li>Lucky's Cozy Home</li></ul>
    <h2>Page Template</h2>
    <div class="bevel card"><h3>{Mod Name}<span class="badge">TEMPLATE</span></h3>
    <h4>What does it add?</h4>""" + fill("Summary") + """
    <h4>Notable Blocks / Items</h4>
    <table><tr><th>Block</th><th>Screenshot</th><th>Notes</th></tr><tr><td></td><td></td><td></td></tr></table>
    <h4>Where to get it</h4>""" + fill("Crafting recipes if custom") + """
    <h4>Tips &amp; Strategies</h4>""" + fill("Build tips") + """
    </div>
    """
    write_page("gameplay/decorations/index.html", "Decorations", content, crumb='<a href="../../index.html">Home</a> / Decorations')

def build_progression():
    content = """
    <p>Probably the single most useful page in the wiki — a linear "what do I do next" path for players.</p>
    <div class="stage-flow">
    <div class="bevel stage"><h3>Day 1</h3><ul class="tasks"><li>Pick starter</li><li>Catch Pokémon</li>
    <li>Build shelter</li><li>Craft Pokéballs</li><li>Find village</li><li>Unlock Waystone</li></ul></div>
    <div class="bevel stage"><h3>Early Game</h3><ul class="tasks"><li>Breed Pokémon</li><li>Collect Apricorns</li>
    <li>Fight Gyms</li><li>Earn CobbleDollars</li></ul></div>
    <div class="bevel stage"><h3>Mid Game</h3><ul class="tasks"><li>Raid Dens</li><li>Collect Megas</li>
    <li>Legendary Hunts</li></ul></div>
    <div class="bevel stage"><h3>Late Game</h3><ul class="tasks"><li>Perfect IVs</li><li>Bottle Caps</li>
    <li>Competitive Teams</li><li>Legendary Collection</li></ul></div>
    </div>
    <div class="callout">Flesh out each bullet with a short paragraph and link to the relevant page once it exists.</div>
    """
    write_page("gameplay/progression-guide.html", "Progression Guide", content, crumb='<a href="../index.html">Home</a> / Progression Guide')

def build_faq():
    faqs = ["How do Pokémon spawn?", "How do raids work?", "How do I Mega Evolve?", "Where do I get Bottle Caps?",
            "How do Badges work?", "Where is my grave?", "How do I claim land?", "Can Pokémon despawn?"]
    content = "<p>Answer each in 1-3 sentences with a link to the full page for more detail.</p>"
    for q in faqs:
        content += f'<div class="bevel card"><h3>{q}</h3>{fill("Short answer + link")}</div>'
    write_page("gameplay/faq.html", "FAQ", content, crumb='<a href="../index.html">Home</a> / FAQ')

def build_rules():
    sections = ["PvP", "Trading", "Economy", "Breeding", "Raids", "Chat", "Exploits"]
    content = ""
    for s in sections:
        note = fill("What counts as an exploit vs. intended mechanic, and consequences.") if s == "Exploits" else fill("Rule text")
        content += f"<h2>{s}</h2>{note}"
    write_page("gameplay/server-rules.html", "Server Rules", content, crumb='<a href="../index.html">Home</a> / Server Rules')

# ---------------------------------------------------------------
def build_technical():
    opt_mods = ["ImmediatelyFast","Lithium","FerriteCore","ModernFix","EntityCulling","MoreCulling",
                "Krypton","C2ME","Debugify","BadOptimizations"]
    opt_rows = "".join(f"<tr><td>{m}</td><td></td></tr>" for m in opt_mods)
    opt_content = f"""
    <p>Most players don't care about these mods, but they'll ask why they're installed. Plain-language explainer.</p>
    <table><tr><th>Mod</th><th>What it improves</th></tr>{opt_rows}</table>
    <h2>Should players change any settings?</h2>{fill("Note anything players can/should tweak client-side.")}
    """
    write_page("technical/optimization.html", "Performance &amp; Optimization", opt_content,
        crumb='<a href="../index.html">Home</a> / Technical / Optimization')

    ctrl_mods = ["Better Third Person","Zoomify","Ping Wheel","Minimap","World Map","REI","Music Controls","BetterF3"]
    ctrl_rows = "".join(f"<tr><td>{m}</td><td></td><td></td></tr>" for m in ctrl_mods)
    ctrl_content = f"""<p>Keybinds added by mods, beyond vanilla Minecraft controls.</p>
    <table><tr><th>Mod</th><th>Default Keybind</th><th>What it does</th></tr>{ctrl_rows}</table>"""
    write_page("technical/controls.html", "Controls Reference", ctrl_content,
        crumb='<a href="../index.html">Home</a> / Technical / Controls')

    admin_pages = [("commands","Commands"),("permissions","Permissions"),("configs","Configs"),
        ("datapacks","Datapacks"),("custom-scripts","Custom Scripts"),("resource-packs","Resource Packs"),
        ("world-generation","World Generation"),("performance-settings","Performance Settings"),
        ("backups","Backups"),("updates","Updates"),("troubleshooting","Troubleshooting")]
    admin_cards = "".join(f'<div class="card bevel"><h3><a href="{slug}.html">{title}</a></h3></div>' for slug, title in admin_pages)
    admin_index = f"""
    <div class="callout"><strong>Internal only.</strong> Keep server secrets (IPs, keys, credentials) out of this
    section if it's ever shared publicly — document what exists and how to change it, not the sensitive values.</div>
    <div class="card-grid">{admin_cards}</div>
    """
    write_page("technical/admin-wiki/index.html", "Admin Wiki", admin_index,
        crumb='<a href="../../index.html">Home</a> / Technical / Admin Wiki')
    for slug, title in admin_pages:
        content = f"""<h2>Overview</h2>{fill("What this covers")}
        <h2>Reference</h2><table><tr><th></th><th></th><th></th></tr><tr><td></td><td></td><td></td></tr></table>
        <h2>Notes / Gotchas</h2><ul class="tasks"><li>{fill("Note")}</li></ul>"""
        write_page(f"technical/admin-wiki/{slug}.html", title, content,
            crumb=f'<a href="../../index.html">Home</a> / Technical / Admin Wiki / {title}')

# ---------------------------------------------------------------
def build_mod_list():
    mod_categories = [
        ("Core Gameplay", ["Cobblemon","CobbleCuisine","Cobbreeding","CobbleDollars","CobbleNav"]),
        ("Battle Extras", ["Battle Positions","Raid Dens","Mega Showdown","Pokeblocks","PastureLoot","SafePastures"]),
        ("Building", ["Beautify","Handcrafted","Rechiseled","Carved Wood","Moar Concrete","Lucky's Cozy Home","CobbleFurnies"]),
        ("Storage", ["Sophisticated Storage","Sophisticated Backpacks","Tom's Storage"]),
        ("Exploration", ["Waystones","Repurposed Structures","Nether Map","Xaero's Minimap","Xaero's World Map","Legendary Monuments"]),
        ("Performance", ["Lithium","ModernFix","FerriteCore","ImmediatelyFast","Krypton","EntityCulling","MoreCulling","C2ME","Debugify","BadOptimizations"]),
        ("Visual", ["Iris","Continuity","Entity Texture Features","Entity Model Features","Particle Rain","Particular","Sound Physics","Zoomify","Not Enough Animations","Better Third Person"]),
    ]
    content = "<p>Grouped by category instead of a flat alphabetical dump. Check off against your actual current mod list, then link each to its wiki page once written.</p>"
    for cat, mods in mod_categories:
        items = "".join(f"<li>{m}</li>" for m in mods)
        content += f'<h2>{cat}</h2><ul class="tasks">{items}</ul>'
    write_page("mod-list.html", "Mod List", content, crumb='<a href="index.html">Home</a> / Mod List')

def build_sources():
    content = """
    <h2>Pokémon Section</h2>
    <p>Combine several authoritative sources rather than relying on one:</p>
    <ul class="tasks">
    <li><strong>Official Cobblemon Wiki</strong> — mechanics, Pokémon data, items, spawning</li>
    <li><strong>Cobblemon's GitLab/GitHub repos</strong> — JSON data for Pokémon, moves, spawn rules, drops, evolutions</li>
    <li><strong>Pokémon Showdown</strong> — competitive movesets and battle data</li>
    <li><strong>Bulbapedia</strong> — canonical Pokémon information</li>
    <li><strong>Serebii</strong> — locations, abilities, learnsets, Pokédex details</li>
    </ul>
    <h2>Non-Pokémon Mods</h2>
    <ul class="tasks">
    <li><strong>CurseForge project pages</strong> — features and changelogs</li>
    <li><strong>Modrinth project pages</strong> — documentation and version compatibility</li>
    <li><strong>GitHub repositories</strong> — configuration options, commands, advanced usage</li>
    <li><strong>Mod authors' own wikis/docs</strong> — when available</li>
    </ul>
    <h2>Server Datapacks (this server)</h2>
    <p>CobbleVerse's own datapacks are the authoritative source for anything server-specific — raid bosses,
    legendary spawn locations, TM recipes, fossils, and LumyMon trades all come straight from
    <code>datapacks.zip</code> via the scripts in <code>/tools</code>.</p>
    <div class="callout"><strong>Automation note.</strong> Most of the Pokémon section, and now several
    Server Features / World pages, can be regenerated straight from datapack JSON — see
    <code>tools/README.md</code> for the extractor scripts.</div>
    """
    write_page("sources.html", "Sources", content, crumb='<a href="index.html">Home</a> / Sources')

def main():
    print("Rebuilding static template pages...")
    build_home()
    build_getting_started()
    build_items_index()
    build_blocks_page()
    build_mechanics()
    build_world()
    build_server_features()
    build_decorations()
    build_progression()
    build_faq()
    build_rules()
    build_technical()
    build_mod_list()
    build_sources()
    print("Done — every static page now reflects the current NAV in site_common.py.")

if __name__ == "__main__":
    main()
