# LenMonu — Legendary Monument screenshots

Drop a screenshot of each monument in this folder and it appears as a
hover preview on the Legendary Monuments page automatically — no rebuild
needed. Name the file exactly after the site slug below, with a .png,
.jpg, .jpeg, or .webp extension (any of the four works):

The same hover-preview component works on any page: wrap text in
`<span class="img-peek" data-img-base="../../assets/images/<folder>/<name>">text</span>`
(path without extension) — or from the build scripts, use the img_peek()
helper in tools/site_common.py.