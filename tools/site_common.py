"""
site_common.py
Shared NAV model + page template for the CobbleVerse wiki generator scripts.
Every generator script (build_site.py, or any future one-off page script)
should import from here so every page keeps the same sidebar and theme.
"""
import os

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../CobbleVerse-Site

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=IBM+Plex+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">')

# ---------------------------------------------------------------
# Nav model: (label, href_or_None, [(child_label, child_href), ...])
# Add new pages here and every page's sidebar picks it up automatically
# next time build_site.py runs.
# ---------------------------------------------------------------
NAV = [
    ("Home", "index.html", None),
    ("Getting Started", None, [
        ("Starter Guide", "gameplay/getting-started/starter-guide.html"),
        ("Controls", "gameplay/getting-started/controls.html"),
        ("Commands", "gameplay/getting-started/commands.html"),
        ("First Pokémon", "gameplay/getting-started/first-pokemon.html"),
        ("Money", "gameplay/getting-started/money.html"),
        ("Badges", "gameplay/getting-started/badges.html"),
        ("Waystones", "gameplay/getting-started/waystones.html"),
        ("Breeding", "gameplay/getting-started/breeding.html"),
        ("Raids", "gameplay/getting-started/raids.html"),
    ]),
    ("Pokémon", "gameplay/pokemon/index.html", None),
    ("Trainers & Gyms", None, [
        ("Overview", "gameplay/trainers/index.html"),
        ("Kanto", "gameplay/trainers/kanto.html"),
        ("Johto", "gameplay/trainers/johto.html"),
        ("Hoenn", "gameplay/trainers/hoenn.html"),
        ("Sinnoh", "gameplay/trainers/sinnoh.html"),
        ("Hisui", "gameplay/trainers/hisui.html"),
        ("Villainous Teams", "gameplay/trainers/villains.html"),
        ("Other Notable Trainers", "gameplay/trainers/other.html"),
    ]),
    ("Items", None, [
        ("Overview", "gameplay/items/index.html"),
        ("TM Crafting", "gameplay/items/tms.html"),
        ("Fossils", "gameplay/items/fossils.html"),
    ]),
    ("Mechanics", None, [
        ("Battle System", "gameplay/mechanics/battle-system.html"),
        ("Status Conditions", "gameplay/mechanics/status-conditions.html"),
        ("Weather", "gameplay/mechanics/weather.html"),
        ("Day/Night Cycle", "gameplay/mechanics/day-night.html"),
        ("Friendship", "gameplay/mechanics/friendship.html"),
        ("Breeding", "gameplay/mechanics/breeding.html"),
        ("Raids", "gameplay/mechanics/raids.html"),
        ("Pastures", "gameplay/mechanics/pastures.html"),
        ("Ride Pokémon", "gameplay/mechanics/ride-pokemon.html"),
        ("Following Pokémon", "gameplay/mechanics/following-pokemon.html"),
        ("Shiny Pokémon", "gameplay/mechanics/shiny-pokemon.html"),
        ("Legendary Spawning", "gameplay/mechanics/legendary-spawning.html"),
        ("Fishing", "gameplay/mechanics/fishing.html"),
        ("Cooking", "gameplay/mechanics/cooking.html"),
    ]),
    ("World", None, [
        ("Biomes", "gameplay/world/biomes.html"),
        ("Structures", "gameplay/world/structures.html"),
        ("Villages", "gameplay/world/villages.html"),
        ("Legendary Monuments", "gameplay/world/legendary-monuments.html"),
        ("Waystones", "gameplay/world/waystones.html"),
        ("Nether", "gameplay/world/nether.html"),
        ("The End", "gameplay/world/the-end.html"),
        ("Custom Builds", "gameplay/world/custom-builds.html"),
    ]),
    ("Server Features", None, [
        ("CobbleDollars", "gameplay/server-features/cobbledollars.html"),
        ("CobbleVerse Badges", "gameplay/server-features/badges.html"),
        ("Legendary Monuments", "gameplay/server-features/legendary-monuments.html"),
        ("Safe Pastures", "gameplay/server-features/safe-pastures.html"),
        ("LumyMon", "gameplay/server-features/lumymon.html"),
        ("CobbleCuisine", "gameplay/server-features/cobblecuisine.html"),
        ("CobbleFurnies", "gameplay/server-features/cobblefurnies.html"),
        ("Economy Overview", "gameplay/server-features/economy.html"),
    ]),
    ("Decorations", "gameplay/decorations/index.html", None),
    ("Progression Guide", "gameplay/progression-guide.html", None),
    ("FAQ", "gameplay/faq.html", None),
    ("Server Rules", "gameplay/server-rules.html", None),
    ("Technical", None, [
        ("Optimization", "technical/optimization.html"),
        ("Controls Reference", "technical/controls.html"),
        ("Admin Wiki", "technical/admin-wiki/index.html"),
    ]),
    ("Mod List", "mod-list.html", None),
    ("Sources", "sources.html", None),
]

def rel(depth, href):
    return ("../" * depth) + href

# Species whose slug->title-case doesn't match their real name (punctuation, etc).
# Shared by extract_data.py (Pokédex names) and build_dynamic_pages.py (trainer team names).
POKEMON_NAME_FIXES = {
    "mrmime": "Mr. Mime", "mrrime": "Mr. Rime", "mimejr": "Mime Jr.",
    "farfetchd": "Farfetch'd", "sirfetchd": "Sirfetch'd",
    "porygonz": "Porygon-Z", "hooh": "Ho-Oh", "jangmoo": "Jangmo-o",
    "hakamoo": "Hakamo-o", "kommoo": "Kommo-o", "typenull": "Type: Null",
    "nidoranf": "Nidoran\u2640", "nidoranm": "Nidoran\u2642",
    "flabebe": "Flab\u00e9b\u00e9", "chienpao": "Chien-Pao", "chiyu": "Chi-Yu",
    "tinglu": "Ting-Lu", "wochien": "Wo-Chien", "greattusk": "Great Tusk",
    "tapukoko": "Tapu Koko", "tapulele": "Tapu Lele", "tapubulu": "Tapu Bulu",
    "tapufini": "Tapu Fini", "porygon2": "Porygon2",
}
def clean_pokemon_name(slug):
    if slug in POKEMON_NAME_FIXES:
        return POKEMON_NAME_FIXES[slug]
    return slug.replace("_", " ").title()

def render_nav(current_href, depth):
    out = []
    for label, href, children in NAV:
        if children is None:
            cur = " current" if href == current_href else ""
            out.append(f'<a class="nav-single{cur}" href="{rel(depth, href)}">{label}</a>')
        else:
            open_attr = ""
            child_html = []
            for clabel, chref in children:
                cur = " current" if chref == current_href else ""
                if chref == current_href:
                    open_attr = " open"
                child_html.append(f'<a class="{"current" if cur else ""}" href="{rel(depth, chref)}">{clabel}</a>')
            out.append(f'<details class="nav-group"{open_attr}><summary>{label}</summary>' + "".join(child_html) + "</details>")
    return "\n".join(out)

PAGE_TMPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} · CobbleVerse Wiki</title>
{fonts}
<link rel="stylesheet" href="{css_href}">
</head>
<body>
<div class="shell">
  <nav class="sidebar">
    <span class="brand">COBBLEVERSE<br>WIKI</span>
    <span class="version-tag">MC 1.21.1 · Cobblemon 1.7.3</span>
    {nav}
  </nav>
  <main>
    <div class="crumb">{crumb}</div>
    <h1>{title}</h1>
    {lede}
    {content}
  </main>
</div>
</body>
</html>
"""

def write_page(path, title, content, crumb="", lede=""):
    full = os.path.join(SITE_ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    depth = path.count("/")
    css_href = rel(depth, "assets/style.css")
    lede_html = f'<p class="lede">{lede}</p>' if lede else ""
    html = PAGE_TMPL.format(
        title=title, fonts=FONTS, css_href=css_href,
        nav=render_nav(path, depth), crumb=crumb, lede=lede_html, content=content,
    )
    with open(full, "w") as f:
        f.write(html)

def fill(label):
    return f'<div class="fill">{label}</div>'

def basic_guide_page(intro):
    return f"""
    <h2>What is it?</h2>{fill("Explain in 2-3 sentences.")}
    <h2>Where do I find it? / How do I start?</h2>{fill("Locations, commands, or crafting path.")}
    <h2>How do I use it?</h2>{fill("Step-by-step, plain language.")}
    <h2>Why should I care?</h2>{fill("What this unlocks or improves for the player.")}
    <h2>Tips &amp; Strategies</h2><ul class="tasks"><li>{fill("Tip one")}</li><li>{fill("Tip two")}</li></ul>
    <h2>Related Pages</h2>{fill("Link related pages once written.")}
    """

def server_feature_page():
    return f"""
    <div class="callout"><strong>Original content.</strong> No external wiki documents this system —
    this page is the only source of truth for players.</div>
    <h2>What is it?</h2>{fill("Explain in 2-3 sentences.")}
    <h2>Where do I find it?</h2>{fill("Menus, commands, in-world locations.")}
    <h2>How do I use it?</h2>{fill("Step-by-step.")}
    <h2>Why should I care?</h2>{fill("The payoff for engaging with this system.")}
    <h2>Tips &amp; Strategies</h2><ul class="tasks"><li>{fill("Tip one")}</li><li>{fill("Tip two")}</li></ul>
    <h2>Common Questions</h2>{fill("Anticipate the first thing players will ask.")}
    <h2>Related Pages</h2>{fill("Link related pages once written.")}
    """
