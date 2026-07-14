# LenMonu — Legendary Monument screenshots

Drop a screenshot of each monument in this folder and it appears as a
hover preview on the Legendary Monuments page automatically — no rebuild
needed. Name the file exactly after the site slug below, with a .png,
.jpg, .jpeg, or .webp extension (any of the four works):

- articuno.png
- bell_tower.png
- burned_tower.png
- celebi_shrine.png
- crescent_isle.png
- crown_cemetery.png
- crown_spire.png
- dawn_tower.png
- deoxys.png
- dusk_tower.png
- dyna_tree.png
- eterna_building.png
- flower_paradise.png
- fullmoon_island.png
- groudon.png
- jirachi.png
- kyogre.png
- manaphy.png
- mew.png
- moltres.png
- regice.png
- regirock.png
- registeel.png
- secret_garden.png
- sky_pillar.png
- snowpoint_temple.png
- spear_pillar.png
- split_decision_temple.png
- whirl_island.png
- wind_plant.png
- zapdos.png

The same hover-preview component works on any page: wrap text in
`<span class="img-peek" data-img-base="../../assets/images/<folder>/<name>">text</span>`
(path without extension) — or from the build scripts, use the img_peek()
helper in tools/site_common.py.