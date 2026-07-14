/* ===========================================================
   CobbleVerse Wiki — site-wide search
   Single JSON index (assets/data/search-index.json) built at
   site-generation time — every page's intro text, plus a
   dedicated entry for each of the 1024 Pokémon and every named
   trainer. Pure client-side substring/prefix scoring, no server.
   =========================================================== */
(function () {
  "use strict";

  var MAX_RESULTS = 9;
  var KIND_LABEL = { page: "Page", pokemon: "Pokémon", trainer: "Trainer" };

  function debounce(fn, ms) {
    var t;
    return function () {
      var args = arguments, ctx = this;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(ctx, args); }, ms);
    };
  }

  function score(entry, q) {
    var title = entry.title.toLowerCase();
    var text = (entry.text || "").toLowerCase();
    if (title === q) return 100;
    if (title.indexOf(q) === 0) return 80;
    if (title.indexOf(q) !== -1) return 60;
    if (text.indexOf(q) !== -1) return 30;
    return 0;
  }

  function init(root) {
    var depth = parseInt(root.getAttribute("data-depth"), 10) || 0;
    var prefix = "../".repeat(depth);
    var input = root.querySelector(".site-search-input");
    var results = root.querySelector(".site-search-results");
    var index = null;
    var hiIndex = -1;
    var currentItems = [];

    fetch(prefix + "assets/data/search-index.json")
      .then(function (r) { return r.json(); })
      .then(function (data) { index = data; })
      .catch(function () { /* search just won't work — rest of the site is unaffected */ });

    function render(items, q) {
      currentItems = items;
      hiIndex = -1;
      if (!items.length) {
        results.innerHTML = '<div class="site-search-empty">No matches for “' + q + '”.</div>';
        results.classList.add("open");
        return;
      }
      results.innerHTML = items.map(function (it, i) {
        var href = prefix + it.url;
        var snippet = (it.text || "").slice(0, 110);
        return '<a class="site-search-result" data-i="' + i + '" href="' + href + '">' +
          '<div class="ssr-title"><span class="ssr-kind">' + KIND_LABEL[it.type] + '</span>' + it.title + '</div>' +
          (it.section ? '<div class="ssr-snippet">' + it.section + '</div>' : (snippet ? '<div class="ssr-snippet">' + snippet + '…</div>' : '')) +
          '</a>';
      }).join("");
      results.classList.add("open");
    }

    function search(q) {
      q = q.trim().toLowerCase();
      if (!q || !index) {
        results.classList.remove("open");
        return;
      }
      var scored = [];
      for (var i = 0; i < index.length; i++) {
        var s = score(index[i], q);
        if (s > 0) scored.push([s, index[i]]);
      }
      scored.sort(function (a, b) { return b[0] - a[0]; });
      render(scored.slice(0, MAX_RESULTS).map(function (s) { return s[1]; }), q);
    }

    var debounced = debounce(function () { search(input.value); }, 100);
    input.addEventListener("input", debounced);
    input.addEventListener("focus", function () { if (input.value.trim()) search(input.value); });

    input.addEventListener("keydown", function (e) {
      var items = results.querySelectorAll(".site-search-result");
      if (e.key === "Escape") {
        results.classList.remove("open");
        input.blur();
      } else if (e.key === "ArrowDown" && items.length) {
        e.preventDefault();
        hiIndex = Math.min(hiIndex + 1, items.length - 1);
        highlight(items);
      } else if (e.key === "ArrowUp" && items.length) {
        e.preventDefault();
        hiIndex = Math.max(hiIndex - 1, 0);
        highlight(items);
      } else if (e.key === "Enter") {
        if (hiIndex >= 0 && items[hiIndex]) {
          location.href = items[hiIndex].getAttribute("href");
        } else if (items.length) {
          location.href = items[0].getAttribute("href");
        }
      }
    });

    function highlight(items) {
      items.forEach(function (el, i) { el.classList.toggle("hi", i === hiIndex); });
      if (items[hiIndex]) items[hiIndex].scrollIntoView({ block: "nearest" });
    }

    document.addEventListener("click", function (e) {
      if (!root.contains(e.target)) results.classList.remove("open");
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var root = document.querySelector(".site-search");
    if (root) init(root);
  });
})();
