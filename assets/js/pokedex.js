/* ===========================================================
   CobbleVerse Wiki — Pokédex engine
   - Loads this pack's own spawn data (assets/data/pokemon.json),
     extracted straight from the server's Cobblemon datapacks.
   - Sprite art loads instantly from the public PokeAPI sprite CDN
     by national dex number (no API call needed for images).
   - Types / abilities / base stats stream in from the live PokeAPI
     in the background, batched and cached in localStorage, so the
     grid is filterable by type without hammering the API and
     repeat visits are instant.
   =========================================================== */
(function () {
  "use strict";

  var CACHE_KEY = "cobbleverse_pokedex_cache_v1";
  var BATCH_SIZE = 40;
  var BATCH_DELAY_MS = 120;

  var GEN_RANGES = [
    [1, 151, "Gen I"], [152, 251, "Gen II"], [252, 386, "Gen III"],
    [387, 493, "Gen IV"], [494, 649, "Gen V"], [650, 721, "Gen VI"],
    [722, 809, "Gen VII"], [810, 905, "Gen VIII"], [906, 1025, "Gen IX"],
  ];
  function genOf(dex) {
    for (var i = 0; i < GEN_RANGES.length; i++) {
      if (dex >= GEN_RANGES[i][0] && dex <= GEN_RANGES[i][1]) return GEN_RANGES[i][2];
    }
    return "Gen ?";
  }

  var TYPES = ["normal","fire","water","electric","grass","ice","fighting","poison",
    "ground","flying","psychic","bug","rock","ghost","dragon","dark","steel","fairy"];

  function spriteUrl(dex) {
    return "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/" + dex + ".png";
  }
  function artworkUrl(dex) {
    return "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/" + dex + ".png";
  }

  function storageAvailable() {
    try {
      var k = "__cobbleverse_test__";
      localStorage.setItem(k, "1");
      localStorage.removeItem(k);
      return true;
    } catch (e) { return false; }
  }

  function loadCache() {
    try {
      var raw = localStorage.getItem(CACHE_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (e) { return {}; }
  }
  function saveCache(cache) {
    try { localStorage.setItem(CACHE_KEY, JSON.stringify(cache)); } catch (e) { /* storage full/blocked — fine, just skip persistence */ }
  }

  function init(root) {
    var dataUrl = root.getAttribute("data-pokemon-json");
    var grid = root.querySelector(".dex-grid");
    var searchInput = root.querySelector(".dex-search");
    var typeRow = root.querySelector(".dex-chip-row.types");
    var genRow = root.querySelector(".dex-chip-row.gens");
    var rarityRow = root.querySelector(".dex-chip-row.rarities");
    var countEl = root.querySelector(".dex-count");
    var progressEl = root.querySelector(".dex-progress");
    var modalBackdrop = document.querySelector(".dex-modal-backdrop");
    var modal = modalBackdrop ? modalBackdrop.querySelector(".dex-modal") : null;

    var cache = loadCache();
    if (!storageAvailable()) {
      var warn = document.createElement("div");
      warn.className = "dex-loading-note";
      warn.style.width = "100%";
      warn.textContent = "Note: this browser is blocking local storage on this page (common when opening the file directly instead of through a web server), so type/stat data will re-download every visit instead of staying cached. Hosting the site (or running a local server) fixes this.";
      root.querySelector(".dex-toolbar").appendChild(warn);
    }
    var state = { q: "", type: null, gen: null, rarity: null };
    var mons = [];

    fetch(dataUrl).then(function (r) { return r.json(); }).then(function (data) {
      mons = data;
      buildFilters();
      renderGrid();
      startEnrichment();
      var params = new URLSearchParams(location.search);
      var deep = params.get("mon");
      if (deep) {
        var m = mons.find(function (x) { return x.slug === deep; });
        if (m) openModal(m);
      }
    }).catch(function (err) {
      grid.innerHTML = '<div class="dex-empty">Could not load Pokédex data (' + err + ').</div>';
    });

    function buildFilters() {
      TYPES.forEach(function (t) {
        var chip = document.createElement("button");
        chip.type = "button";
        chip.className = "dex-chip";
        chip.textContent = t;
        chip.addEventListener("click", function () {
          state.type = state.type === t ? null : t;
          syncChipRow(typeRow, chip);
          renderGrid();
        });
        typeRow.appendChild(chip);
      });
      GEN_RANGES.forEach(function (g) {
        var chip = document.createElement("button");
        chip.type = "button";
        chip.className = "dex-chip";
        chip.textContent = g[2];
        chip.addEventListener("click", function () {
          state.gen = state.gen === g[2] ? null : g[2];
          syncChipRow(genRow, chip);
          renderGrid();
        });
        genRow.appendChild(chip);
      });
      ["common", "uncommon", "rare", "ultra-rare"].forEach(function (r) {
        var chip = document.createElement("button");
        chip.type = "button";
        chip.className = "dex-chip";
        chip.textContent = r;
        chip.addEventListener("click", function () {
          state.rarity = state.rarity === r ? null : r;
          syncChipRow(rarityRow, chip);
          renderGrid();
        });
        rarityRow.appendChild(chip);
      });
      searchInput.addEventListener("input", function () {
        state.q = searchInput.value.trim().toLowerCase();
        renderGrid();
      });
    }

    function syncChipRow(row, active) {
      var wasActive = active.classList.contains("active");
      Array.prototype.forEach.call(row.children, function (c) { c.classList.remove("active"); });
      if (!wasActive) { active.classList.add("active"); }
    }

    function matches(m) {
      if (state.q) {
        var hay = m.name.toLowerCase() + " " + String(m.dex);
        if (hay.indexOf(state.q) === -1) return false;
      }
      if (state.gen && genOf(m.dex) !== state.gen) return false;
      if (state.rarity && m.best_bucket !== state.rarity) return false;
      if (state.type) {
        var c = cache[m.dex];
        if (!c || !c.types || c.types.indexOf(state.type) === -1) return false;
      }
      return true;
    }

    function renderGrid() {
      grid.innerHTML = "";
      var shown = 0;
      var frag = document.createDocumentFragment();
      mons.forEach(function (m) {
        if (!matches(m)) return;
        shown++;
        frag.appendChild(cardFor(m));
      });
      if (shown === 0) {
        grid.innerHTML = '<div class="dex-empty">No Pokémon match those filters.</div>';
      } else {
        grid.appendChild(frag);
      }
      countEl.textContent = shown + " / " + mons.length + " shown";
    }

    function cardFor(m) {
      var card = document.createElement("div");
      card.className = "dex-card";
      card.setAttribute("data-dex", m.dex);
      var typesHtml = typePillsHtml(cache[m.dex] && cache[m.dex].types);
      card.innerHTML =
        '<div class="dex-num">#' + String(m.dex).padStart(4, "0") + '</div>' +
        '<img loading="lazy" src="' + spriteUrl(m.dex) + '" alt="' + m.name + '" onerror="this.style.visibility=\'hidden\'">' +
        '<div class="dex-name">' + m.name + '</div>' +
        '<div class="dex-types">' + typesHtml + '</div>';
      card.addEventListener("click", function () { openModal(m); });
      return card;
    }

    function typePillsHtml(types) {
      if (!types) return "";
      return types.map(function (t) {
        return '<span class="type-pill type-' + t + '">' + t + '</span>';
      }).join("");
    }

    function startEnrichment() {
      var toFetch = [];
      mons.forEach(function (m) {
        if (cache[m.dex]) { updateCardTypes(m); }
        else { toFetch.push(m); }
      });
      if (toFetch.length === 0) {
        progressEl.classList.remove("active");
        return; // everything was already cached from a previous visit — nothing to do
      }
      toFetch.sort(function (a, b) { return a.dex - b.dex; });
      var i = 0;
      var total = toFetch.length;
      var done = 0;
      progressEl.classList.add("active");
      function nextBatch() {
        if (i >= total) {
          progressEl.classList.remove("active");
          saveCache(cache);
          return;
        }
        var batch = toFetch.slice(i, i + BATCH_SIZE);
        i += BATCH_SIZE;
        Promise.all(batch.map(fetchOne)).then(function () {
          done += batch.length;
          progressEl.textContent = "Loading live type/stat data from PokeAPI… " + Math.min(done, total) + " / " + total + " new (rest are cached)";
          saveCache(cache);
          setTimeout(nextBatch, BATCH_DELAY_MS);
        });
      }
      nextBatch();
    }

    function fetchOne(m) {
      if (cache[m.dex]) { updateCardTypes(m); return Promise.resolve(); }
      return fetch("https://pokeapi.co/api/v2/pokemon/" + m.dex + "/")
        .then(function (r) { if (!r.ok) throw new Error("bad status"); return r.json(); })
        .then(function (d) {
          cache[m.dex] = {
            types: d.types.map(function (t) { return t.type.name; }),
            abilities: d.abilities.map(function (a) { return { name: a.ability.name, hidden: a.is_hidden }; }),
            stats: d.stats.reduce(function (acc, s) { acc[s.stat.name] = s.base_stat; return acc; }, {}),
            height: d.height, weight: d.weight,
          };
          updateCardTypes(m);
        })
        .catch(function () { /* network hiccup or unmapped form — leave uncached, grid still usable */ });
    }

    function updateCardTypes(m) {
      var card = grid.querySelector('.dex-card[data-dex="' + m.dex + '"]');
      if (!card) return;
      var el = card.querySelector(".dex-types");
      if (el) el.innerHTML = typePillsHtml(cache[m.dex] && cache[m.dex].types);
    }

    function statLabel(k) {
      return { hp: "HP", attack: "Atk", defense: "Def", "special-attack": "SpA",
        "special-defense": "SpD", speed: "Spe" }[k] || k;
    }

    function openModal(m) {
      if (!modalBackdrop) return;
      var c = cache[m.dex];
      var url = new URL(location.href);
      url.searchParams.set("mon", m.slug);
      history.replaceState(null, "", url);

      var typesHtml = c ? typePillsHtml(c.types) :
        '<span class="dex-loading-note">Fetching type data…</span>';
      var abilitiesHtml = c ?
        c.abilities.map(function (a) { return a.name.replace(/-/g, " ") + (a.hidden ? " (Hidden)" : ""); }).join(", ") :
        '<span class="dex-loading-note">loading…</span>';
      var statsHtml = c ? Object.keys(c.stats).map(function (k) {
        var v = c.stats[k];
        var pct = Math.min(100, Math.round((v / 180) * 100));
        return '<div class="dex-stat-row"><span>' + statLabel(k) + '</span>' +
          '<div class="dex-stat-bar"><div class="dex-stat-fill" style="width:' + pct + '%"></div></div>' +
          '<span class="mono">' + v + '</span></div>';
      }).join("") : '<span class="dex-loading-note">Base stats load in the background — check back in a moment, or reopen this card.</span>';

      var spawnHtml = (m.spawns || []).map(function (s) {
        var bits = [];
        if (s.bucket) bits.push('<span class="rarity-pill rarity-' + s.bucket + '">' + s.bucket + '</span>');
        if (s.position) bits.push(s.position);
        if (s.level_min != null) bits.push("Lv " + s.level_min + (s.level_max && s.level_max !== s.level_min ? "–" + s.level_max : ""));
        if (s.time) bits.push(s.time);
        if (s.weather) bits.push(s.weather);
        var biomes = (s.biomes || []).join(", ");
        return '<div class="dex-spawn-block">' + bits.join(" · ") +
          (biomes ? '<br><span class="mono">' + biomes + '</span>' : '') +
          (s.presets && s.presets.length && s.presets[0] !== "natural" ? '<br><span class="mono">' + s.presets.join(", ") + '</span>' : '') +
          '</div>';
      }).join("") || '<p class="dex-loading-note">No world spawn data for this species in the current datapacks (may be event/gift/evolution-only).</p>';

      modal.innerHTML =
        '<button class="dex-modal-close" aria-label="Close">×</button>' +
        '<div class="dex-modal-head">' +
        '<img src="' + artworkUrl(m.dex) + '" alt="' + m.name + '" onerror="this.src=\'' + spriteUrl(m.dex) + '\'">' +
        '<div><h2>#' + String(m.dex).padStart(4, "0") + ' ' + m.name + '</h2>' +
        '<div class="dex-modal-types">' + typesHtml + '</div>' +
        '<div class="dex-modal-sub">Abilities: ' + abilitiesHtml + '</div>' +
        '</div></div>' +
        '<h3 style="margin-top:1.25rem;">Base Stats</h3>' + statsHtml +
        '<h3>Spawn Data <span class="badge">from this server\u2019s datapacks</span></h3>' + spawnHtml;

      modal.querySelector(".dex-modal-close").addEventListener("click", closeModal);
      modalBackdrop.classList.add("open");

      if (!c) {
        var wait = setInterval(function () {
          if (cache[m.dex]) { clearInterval(wait); if (modalBackdrop.classList.contains("open")) openModal(m); }
        }, 500);
      }
    }

    function closeModal() {
      modalBackdrop.classList.remove("open");
      var url = new URL(location.href);
      url.searchParams.delete("mon");
      history.replaceState(null, "", url);
    }

    if (modalBackdrop) {
      modalBackdrop.addEventListener("click", function (e) {
        if (e.target === modalBackdrop) closeModal();
      });
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") closeModal();
      });
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    var root = document.querySelector("[data-pokedex-root]");
    if (root) init(root);
  });
})();
