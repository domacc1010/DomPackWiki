/* ===========================================================
   CobbleVerse Wiki — Advanced Search results page
   Loads the same search-index.json as the sidebar search, but
   shows every match with type + section filters instead of a
   capped dropdown. Reads ?q= from the URL on load.
   =========================================================== */
(function () {
  "use strict";

  var TYPE_LABEL = { page: "Page", pokemon: "Pokémon", trainer: "Trainer", item: "Item" };

  function init(root) {
    var depth = parseInt(root.getAttribute("data-depth"), 10) || 0;
    var prefix = "../".repeat(depth);
    var input = root.querySelector(".dex-search");
    var typeRow = root.querySelector(".dex-chip-row.types");
    var sectionRow = root.querySelector(".dex-chip-row.sections");
    var list = root.querySelector(".adv-result-list");
    var countEl = root.querySelector(".dex-count");

    var index = [];
    var state = { q: "", type: null, section: null };

    fetch(prefix + "assets/data/search-index.json").then(function (r) { return r.json(); })
      .then(function (data) {
        index = data;
        var params = new URLSearchParams(location.search);
        var q = params.get("q") || "";
        input.value = q;
        state.q = q.toLowerCase();
        buildTypeChips();
        render();
      })
      .catch(function () {
        list.innerHTML = '<div class="dex-empty">Could not load the search index.</div>';
      });

    input.addEventListener("input", function () {
      state.q = input.value.trim().toLowerCase();
      var url = new URL(location.href);
      if (state.q) url.searchParams.set("q", state.q); else url.searchParams.delete("q");
      history.replaceState(null, "", url);
      render();
    });

    function buildTypeChips() {
      var types = [];
      index.forEach(function (e) { if (types.indexOf(e.type) === -1) types.push(e.type); });
      typeRow.innerHTML = "";
      types.forEach(function (t) {
        var chip = document.createElement("button");
        chip.type = "button";
        chip.className = "dex-chip";
        chip.textContent = TYPE_LABEL[t] || t;
        chip.setAttribute("data-val", t);
        chip.addEventListener("click", function () {
          state.type = state.type === t ? null : t;
          state.section = null; // section list depends on type, reset it
          syncChipRow(typeRow, state.type);
          buildSectionChips();
          render();
        });
        typeRow.appendChild(chip);
      });
    }

    function buildSectionChips() {
      sectionRow.innerHTML = "";
      if (!state.type) return; // section filter only makes sense once a type is picked
      var pool = index.filter(function (e) { return e.type === state.type; });
      var sections = [];
      pool.forEach(function (e) { if (e.section && sections.indexOf(e.section) === -1) sections.push(e.section); });
      sections.sort();
      if (sections.length > 30) return; // e.g. individual Pokémon sections aren't meaningfully filterable this way
      sections.forEach(function (s) {
        var chip = document.createElement("button");
        chip.type = "button";
        chip.className = "dex-chip";
        chip.textContent = s;
        chip.setAttribute("data-val", s);
        chip.addEventListener("click", function () {
          state.section = state.section === s ? null : s;
          syncChipRow(sectionRow, state.section);
          render();
        });
        sectionRow.appendChild(chip);
      });
    }

    function syncChipRow(row, activeValue) {
      Array.prototype.forEach.call(row.children, function (c) {
        c.classList.toggle("active", c.getAttribute("data-val") === activeValue);
        c.blur();
      });
    }

    function score(e, q) {
      var title = e.title.toLowerCase();
      var text = ((e.text || "") + " " + (e.section || "")).toLowerCase();
      if (!q) return 1;
      if (title === q) return 100;
      if (title.indexOf(q) === 0) return 80;
      if (title.indexOf(q) !== -1) return 60;
      if (text.indexOf(q) !== -1) return 30;
      return 0;
    }

    function render() {
      var q = state.q;
      var scored = [];
      for (var i = 0; i < index.length; i++) {
        var e = index[i];
        if (state.type && e.type !== state.type) continue;
        if (state.section && e.section !== state.section) continue;
        var s = score(e, q);
        if (s > 0) scored.push([s, e]);
      }
      scored.sort(function (a, b) { return b[0] - a[0]; });
      var results = scored.map(function (s) { return s[1]; });

      countEl.textContent = results.length + " result" + (results.length === 1 ? "" : "s");
      if (!results.length) {
        list.innerHTML = '<div class="dex-empty">No matches' + (q ? ' for "' + q + '"' : '') + '. Try a different term or clear filters.</div>';
        return;
      }
      list.innerHTML = results.slice(0, 300).map(function (e) {
        var snippet = (e.text || "").slice(0, 180);
        return '<a class="adv-result-row" href="' + e.url + '">' +
          '<div class="adv-result-top"><span class="dex-chip item-cat-pill" style="cursor:default;">' + (TYPE_LABEL[e.type] || e.type) + '</span>' +
          '<span class="adv-result-title">' + e.title + '</span></div>' +
          (e.section ? '<div class="adv-result-section">' + e.section + '</div>' : '') +
          (snippet ? '<div class="adv-result-snippet">' + snippet + (e.text && e.text.length > 180 ? '…' : '') + '</div>' : '') +
          '</a>';
      }).join("");
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    var root = document.querySelector("[data-search-root]");
    if (root) init(root);
  });
})();
