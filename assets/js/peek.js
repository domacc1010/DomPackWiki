/* ===========================================================
   CobbleVerse Wiki — image peek component
   Hover any element with class="img-peek" and a data-img-base
   attribute to get a small floating image preview; hover the
   preview itself to enlarge it; click the preview to open the
   full image in a new tab.

   Usage (works on any page, any element):
     <span class="img-peek" data-img-base="../../assets/images/LenMonu/sky_pillar">
       Sky Pillar
     </span>

   data-img-base is the image path WITHOUT extension — .png,
   .jpg, .jpeg, and .webp are tried in that order, so it doesn't
   matter which format the screenshot was saved in. If no image
   exists at that base path, hovering simply shows nothing (no
   broken-image icon), so markup can be added before the
   screenshot is taken.

   On touch devices (no hover), tapping the text toggles the
   preview and tapping the preview enlarges it.
   =========================================================== */
(function () {
  "use strict";

  var EXTENSIONS = [".png", ".jpg", ".jpeg", ".webp"];
  var HIDE_DELAY_MS = 140;

  var pop = null;
  var popImg = null;
  var hideTimer = null;
  var currentBase = null;

  function ensurePop() {
    if (pop) return;
    pop = document.createElement("div");
    pop.id = "img-peek-pop";
    popImg = document.createElement("img");
    popImg.alt = "";
    pop.appendChild(popImg);
    document.body.appendChild(pop);

    pop.addEventListener("mouseenter", function () {
      cancelHide();
      pop.classList.add("big");
      clampToViewport();
    });
    pop.addEventListener("mouseleave", function () {
      pop.classList.remove("big");
      scheduleHide();
    });
    pop.addEventListener("click", function () {
      if (popImg.src) window.open(popImg.src, "_blank", "noopener");
    });
  }

  function tryLoad(base, extIndex, onOk, onFail) {
    if (extIndex >= EXTENSIONS.length) { onFail(); return; }
    var probe = new Image();
    probe.onload = function () { onOk(base + EXTENSIONS[extIndex]); };
    probe.onerror = function () { tryLoad(base, extIndex + 1, onOk, onFail); };
    probe.src = base + EXTENSIONS[extIndex];
  }

  function showFor(trigger) {
    var base = trigger.getAttribute("data-img-base");
    if (!base) return;
    ensurePop();
    cancelHide();
    currentBase = base;

    tryLoad(base, 0, function (url) {
      if (currentBase !== base) return; // hovered something else meanwhile
      popImg.src = url;
      pop.classList.remove("big");
      pop.classList.add("open");
      position(trigger);
    }, function () {
      if (currentBase !== base) return;
      hideNow(); // no image found at any extension — show nothing
    });
  }

  function position(trigger) {
    var r = trigger.getBoundingClientRect();
    pop.style.left = Math.round(r.left) + "px";
    pop.style.top = Math.round(r.bottom + 6) + "px";
    clampToViewport();
  }

  function clampToViewport() {
    if (!pop || !pop.classList.contains("open")) return;
    // Let it render, then pull it back inside the viewport if it overflows.
    requestAnimationFrame(function () {
      var pr = pop.getBoundingClientRect();
      var newLeft = pr.left, newTop = pr.top;
      if (pr.right > window.innerWidth - 8) newLeft = Math.max(8, window.innerWidth - 8 - pr.width);
      if (pr.bottom > window.innerHeight - 8) newTop = Math.max(8, window.innerHeight - 8 - pr.height);
      pop.style.left = Math.round(newLeft) + "px";
      pop.style.top = Math.round(newTop) + "px";
    });
  }

  function scheduleHide() {
    cancelHide();
    hideTimer = setTimeout(hideNow, HIDE_DELAY_MS);
  }
  function cancelHide() {
    if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }
  }
  function hideNow() {
    cancelHide();
    currentBase = null;
    if (pop) {
      pop.classList.remove("open", "big");
      popImg.removeAttribute("src");
    }
  }

  // Event delegation — works for content added after load too.
  document.addEventListener("mouseover", function (e) {
    var t = e.target.closest && e.target.closest(".img-peek");
    if (t) showFor(t);
  });
  document.addEventListener("mouseout", function (e) {
    var t = e.target.closest && e.target.closest(".img-peek");
    if (t && !(e.relatedTarget && (e.relatedTarget.closest(".img-peek") === t ||
        (pop && pop.contains(e.relatedTarget))))) {
      scheduleHide();
    }
  });

  // Touch support: tap text toggles preview; tap preview enlarges (click
  // handler above also opens full image, which on touch is the second tap).
  document.addEventListener("click", function (e) {
    var t = e.target.closest && e.target.closest(".img-peek");
    if (t) {
      if (pop && pop.classList.contains("open") && currentBase === t.getAttribute("data-img-base")) {
        hideNow();
      } else {
        showFor(t);
      }
    } else if (pop && !pop.contains(e.target)) {
      hideNow();
    }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") hideNow();
  });
  window.addEventListener("scroll", hideNow, { passive: true });
})();
