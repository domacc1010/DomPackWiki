/* ===========================================================
   CobbleVerse Wiki — Item Database engine
   Same search/filter/grid pattern as the Pokédex, for items.
   All data is local (assets/data/items.json) — no external API,
   so this is instant with no background loading.
   =========================================================== */
(function () {
  "use strict";

  function init(root) {
    var dataUrl = root.getAttribute("data-items-json");
    var grid = root.querySelector(".dex-grid");
    var searchInput = root.querySelector(".dex-search");
    var catRow = root.querySelector(".dex-chip-row.categories");
    var countEl = root.querySelector(".dex-count");

    var state = { q: "", category: null };
    var items = [];

    fetch(dataUrl).then(function (r) { return r.json(); }).then(function (data) {
      items = data;
      buildFilters();
      renderGrid();
      var params = new URLSearchParams(location.search);
      var q = params.get("q");
      if (q) { searchInput.value = q; state.q = q.toLowerCase(); renderGrid(); }
    }).catch(function (err) {
      grid.innerHTML = '<div class="dex-empty">Could not load item data (' + err + ').</div>';
    });

    function buildFilters() {
      var cats = [];
      items.forEach(function (it) { if (cats.indexOf(it.category) === -1) cats.push(it.category); });
      cats.sort();
      cats.forEach(function (cat) {
        var chip = document.createElement("button");
        chip.type = "button";
        chip.className = "dex-chip";
        chip.textContent = cat;
        chip.setAttribute("data-val", cat);
        chip.addEventListener("click", function () {
          state.category = state.category === cat ? null : cat;
          syncChipRow(catRow, state.category);
          renderGrid();
        });
        catRow.appendChild(chip);
      });
      searchInput.addEventListener("input", function () {
        state.q = searchInput.value.trim().toLowerCase();
        renderGrid();
      });
    }

    function syncChipRow(row, activeValue) {
      Array.prototype.forEach.call(row.children, function (c) {
        c.classList.toggle("active", c.getAttribute("data-val") === activeValue);
        c.blur();
      });
    }

    function matches(it) {
      if (state.category && it.category !== state.category) return false;
      if (state.q) {
        var hay = (it.name + " " + it.category + " " + (it.desc || "")).toLowerCase();
        if (hay.indexOf(state.q) === -1) return false;
      }
      return true;
    }

    function renderGrid() {
      grid.innerHTML = "";
      var shown = 0;
      var frag = document.createDocumentFragment();
      items.forEach(function (it) {
        if (!matches(it)) return;
        shown++;
        frag.appendChild(cardFor(it));
      });
      if (shown === 0) {
        grid.innerHTML = '<div class="dex-empty">No items match those filters.</div>';
      } else {
        grid.appendChild(frag);
      }
      countEl.textContent = shown + " / " + items.length + " shown";
    }

    function cardFor(it) {
      var card = document.createElement("div");
      card.className = "item-card";
      card.innerHTML =
        '<div class="item-card-head"><span class="item-name">' + it.name + '</span>' +
        '<span class="dex-chip item-cat-pill">' + it.category + '</span></div>' +
        (it.desc ? '<p class="item-desc">' + it.desc + '</p>' : '<p class="item-desc dex-loading-note">No summary yet.</p>') +
        '<a class="item-wiki-link" href="' + it.wiki_url + '" target="_blank" rel="noopener">Full details on the official Cobblemon Wiki \u2197</a>';
      return card;
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    var root = document.querySelector("[data-items-root]");
    if (root) init(root);
  });
})();
