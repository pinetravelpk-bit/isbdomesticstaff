/* ISB Domestic Staff — interactions & animations */
(function () {
  "use strict";

  var WHATSAPP = "923105214309";
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ---------- Image fallbacks: drawn art if a stock photo fails ---------- */
  var FALLBACK = {
    maid: ["#dbeafe", "#1f8bff", "M50 30a10 10 0 1 1 0 .1M34 80c0-14 7-24 16-24s16 10 16 24z"],
    housekeeper: ["#ccfbf1", "#0d9488", "M50 30a10 10 0 1 1 0 .1M34 80c0-14 7-24 16-24s16 10 16 24zM62 60h16v12H62z"],
    cook: ["#fef3c7", "#f59e0b", "M38 26a8 8 0 0 1 12-6 8 8 0 0 1 12 6 7 7 0 0 1-4 13H42a7 7 0 0 1-4-13zM50 50a8 8 0 1 1 0 .1M36 84c0-12 6-20 14-20s14 8 14 20z"],
    driver: ["#e0e7ff", "#0b3d7a", "M22 62l8-18h40l8 18v12H22zM32 74a5 5 0 1 0 0 .1M68 74a5 5 0 1 0 0 .1"],
    office: ["#dbeafe", "#0b3d7a", "M50 30a10 10 0 1 1 0 .1M34 80c0-14 7-24 16-24s16 10 16 24zM46 56l4 10 4-10"],
    cleaner: ["#cffafe", "#0891b2", "M50 30a10 10 0 1 1 0 .1M34 80c0-14 7-24 16-24s16 10 16 24zM72 40v40M66 80h12"],
    watchman: ["#e2e8f0", "#0f1f3a", "M50 18l18 7v10c0 12-8 20-18 24-10-4-18-12-18-24V25zM44 38l5 5 9-9"],
    babysitter: ["#ffe4e6", "#f43f5e", "M50 68l-14-14a8 8 0 0 1 14-10 8 8 0 0 1 14 10z"],
    care: ["#dcfce7", "#16a34a", "M44 26h12v14h14v12H56v14H44V52H30V40h14z"],
    family: ["#e0f2fe", "#0b3d7a", "M36 34a8 8 0 1 1 0 .1M64 34a8 8 0 1 1 0 .1M50 52a6 6 0 1 1 0 .1M22 80c0-12 6-22 14-22s14 10 14 22M50 80c0-12 6-22 14-22s14 10 14 22"],
    avatar: ["#dbeafe", "#1f8bff", "M50 36a12 12 0 1 1 0 .1M28 84c0-16 10-26 22-26s22 10 22 26z"],
    room: ["#0b3d7a", "#127fa8", "M10 70h80v10H10zM20 50h60v20H20z"]
  };
  function fallbackSrc(kind) {
    var f = FALLBACK[kind] || FALLBACK.avatar;
    var svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid slice">' +
      '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="' + f[0] + '"/><stop offset="1" stop-color="#ffffff"/></linearGradient></defs>' +
      '<rect width="100" height="100" fill="url(#g)"/><circle cx="82" cy="18" r="14" fill="' + f[1] + '" opacity=".12"/>' +
      '<path d="' + f[2] + '" fill="' + f[1] + '" opacity=".85"/></svg>';
    return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
  }
  function applyFallback(img) {
    if (img.dataset.fellBack) return;
    img.dataset.fellBack = "1";
    img.classList.add("is-fallback");
    img.src = fallbackSrc(img.dataset.fallback);
  }
  $$("img[data-fallback]").forEach(function (img) {
    img.addEventListener("error", function () { applyFallback(img); });
    if (img.complete && img.naturalWidth === 0 && img.currentSrc) applyFallback(img);
  });

  /* ---------- Marquee: duplicate items for a seamless loop ---------- */
  var mq = $(".marquee__track");
  if (mq) $$("span", mq).forEach(function (s) { var c = s.cloneNode(true); c.setAttribute("aria-hidden", "true"); mq.appendChild(c); });

  /* ---------- Preloader ---------- */
  function hidePreloader() { var p = $("#preloader"); if (p) p.classList.add("is-done"); }
  window.addEventListener("load", function () { setTimeout(hidePreloader, 300); });
  setTimeout(hidePreloader, 2500); // never block the page on slow images

  /* ---------- Header, progress bar, back-to-top ---------- */
  var header = $("#header"), progress = $("#progress"), toTop = $("#toTop");
  function onScroll() {
    var y = window.scrollY, h = document.documentElement.scrollHeight - window.innerHeight;
    header.classList.toggle("is-scrolled", y > 20);
    progress.style.width = (h > 0 ? (y / h) * 100 : 0) + "%";
    toTop.classList.toggle("is-shown", y > 600);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  toTop.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });

  /* ---------- Mobile menu ---------- */
  var burger = $("#burger"), nav = $("#nav");
  function setMenu(open) {
    burger.classList.toggle("is-open", open);
    nav.classList.toggle("is-open", open);
    burger.setAttribute("aria-expanded", String(open));
  }
  burger.addEventListener("click", function () { setMenu(!nav.classList.contains("is-open")); });
  $$("#nav a").forEach(function (a) { a.addEventListener("click", function () { setMenu(false); }); });

  /* ---------- Active nav link on scroll ---------- */
  var links = $$(".nav__link");
  var sections = links.map(function (l) { return $(l.getAttribute("href")); }).filter(Boolean);
  if ("IntersectionObserver" in window) {
    var navObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        links.forEach(function (l) { l.classList.toggle("is-active", l.getAttribute("href") === "#" + e.target.id); });
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    sections.forEach(function (s) { navObs.observe(s); });
  }

  /* ---------- Scroll reveal ---------- */
  var revealEls = $$(".reveal, .reveal-left, .steps");
  if ("IntersectionObserver" in window && !reduceMotion) {
    var rObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var d = parseInt(e.target.dataset.delay || 0, 10);
        setTimeout(function () { e.target.classList.add("is-visible"); }, d);
        rObs.unobserve(e.target);
      });
    }, { threshold: 0.15, rootMargin: "0px 0px -40px 0px" });
    revealEls.forEach(function (el) { rObs.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* ---------- Typing effect ---------- */
  var typer = $("#typer");
  var words = ["maids", "housekeepers", "cooks", "drivers", "babysitters", "patient attendants", "watchmen"];
  if (typer && !reduceMotion) {
    var wi = 0, ci = words[0].length, deleting = true;
    (function tick() {
      var w = words[wi];
      ci += deleting ? -1 : 1;
      typer.textContent = w.slice(0, ci);
      var wait = deleting ? 45 : 85;
      if (!deleting && ci === w.length) { deleting = true; wait = 1700; }
      else if (deleting && ci === 0) { deleting = false; wi = (wi + 1) % words.length; wait = 300; }
      setTimeout(tick, wait);
    })();
  }

  /* ---------- Animated counters ---------- */
  function animateCount(el) {
    var to = parseInt(el.dataset.to, 10), start = null, dur = 2000;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1), eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(to * eased).toLocaleString("en-US");
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  var counters = $$(".count");
  if ("IntersectionObserver" in window && !reduceMotion) {
    var cObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { animateCount(e.target); cObs.unobserve(e.target); } });
    }, { threshold: 0.6 });
    counters.forEach(function (c) { cObs.observe(c); });
  } else {
    counters.forEach(function (c) { c.textContent = parseInt(c.dataset.to, 10).toLocaleString("en-US"); });
  }

  /* ---------- Testimonial slider ---------- */
  var slider = $("#slider");
  if (slider) {
    var track = $(".slider__track", slider), cards = $$(".t-card", slider), dotsWrap = $(".slider__dots", slider);
    var index = 0, timer;
    function perView() { return window.innerWidth <= 640 ? 1 : window.innerWidth <= 980 ? 2 : 3; }
    function maxIndex() { return Math.max(0, cards.length - perView()); }
    function buildDots() {
      dotsWrap.innerHTML = "";
      for (var i = 0; i <= maxIndex(); i++) {
        var b = document.createElement("button");
        b.type = "button"; b.setAttribute("aria-label", "Go to slide " + (i + 1));
        b.addEventListener("click", (function (n) { return function () { go(n); restart(); }; })(i));
        dotsWrap.appendChild(b);
      }
    }
    function go(n) {
      index = n > maxIndex() ? 0 : n < 0 ? maxIndex() : n;
      var gap = parseFloat(getComputedStyle(track).gap) || 0;
      track.style.transform = "translateX(" + -(index * (cards[0].offsetWidth + gap)) + "px)";
      $$("button", dotsWrap).forEach(function (d, i) { d.classList.toggle("is-active", i === index); });
    }
    function restart() { clearInterval(timer); if (!reduceMotion) timer = setInterval(function () { go(index + 1); }, 5000); }
    $(".slider__btn--next", slider).addEventListener("click", function () { go(index + 1); restart(); });
    $(".slider__btn--prev", slider).addEventListener("click", function () { go(index - 1); restart(); });
    slider.addEventListener("mouseenter", function () { clearInterval(timer); });
    slider.addEventListener("mouseleave", restart);
    // swipe
    var sx = null;
    slider.addEventListener("touchstart", function (e) { sx = e.touches[0].clientX; }, { passive: true });
    slider.addEventListener("touchend", function (e) {
      if (sx === null) return;
      var dx = e.changedTouches[0].clientX - sx;
      if (Math.abs(dx) > 40) { go(index + (dx < 0 ? 1 : -1)); restart(); }
      sx = null;
    });
    window.addEventListener("resize", function () { buildDots(); go(Math.min(index, maxIndex())); });
    buildDots(); go(0); restart();
  }

  /* ---------- 3D tilt on service cards ---------- */
  var finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (finePointer && !reduceMotion) {
    $$(".tilt").forEach(function (card) {
      card.addEventListener("mousemove", function (e) {
        var r = card.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
        card.style.transform = "perspective(800px) rotateX(" + (-y * 10) + "deg) rotateY(" + (x * 10) + "deg) translateY(-8px)";
      });
      card.addEventListener("mouseleave", function () { card.style.transform = ""; });
    });

    /* Magnetic buttons */
    $$(".magnetic").forEach(function (btn) {
      btn.addEventListener("mousemove", function (e) {
        var r = btn.getBoundingClientRect();
        btn.style.transform = "translate(" + (e.clientX - r.left - r.width / 2) * 0.18 + "px," + (e.clientY - r.top - r.height / 2) * 0.3 + "px)";
      });
      btn.addEventListener("mouseleave", function () { btn.style.transform = ""; });
    });

    /* Hero parallax on mouse move */
    var hero = $("#heroVisual");
    if (hero) {
      var layers = $$(".parallax", hero);
      document.addEventListener("mousemove", function (e) {
        var cx = e.clientX - window.innerWidth / 2, cy = e.clientY - window.innerHeight / 2;
        layers.forEach(function (l) {
          var s = parseFloat(l.dataset.speed);
          l.style.transform = "translate(" + cx * s + "px," + cy * s + "px)";
        });
      });
    }
  }

  /* ---------- Hero particles ---------- */
  var canvas = $("#particles");
  if (canvas && canvas.getContext && !reduceMotion) {
    var ctx = canvas.getContext("2d"), dots = [], W, H, dpr = Math.min(window.devicePixelRatio || 1, 2);
    function size() {
      W = canvas.offsetWidth; H = canvas.offsetHeight;
      canvas.width = W * dpr; canvas.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      var n = Math.round(Math.min(60, W / 22));
      dots = [];
      for (var i = 0; i < n; i++) {
        dots.push({ x: Math.random() * W, y: Math.random() * H, r: Math.random() * 2.2 + 0.8, vx: (Math.random() - 0.5) * 0.35, vy: (Math.random() - 0.5) * 0.35, c: Math.random() > 0.8 ? "255,106,61" : "31,139,255" });
      }
    }
    function draw() {
      ctx.clearRect(0, 0, W, H);
      for (var i = 0; i < dots.length; i++) {
        var d = dots[i];
        d.x += d.vx; d.y += d.vy;
        if (d.x < 0 || d.x > W) d.vx *= -1;
        if (d.y < 0 || d.y > H) d.vy *= -1;
        ctx.beginPath(); ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(" + d.c + ",.35)"; ctx.fill();
        for (var j = i + 1; j < dots.length; j++) {
          var e = dots[j], dx = d.x - e.x, dy = d.y - e.y, dist = dx * dx + dy * dy;
          if (dist < 12000) {
            ctx.strokeStyle = "rgba(31,139,255," + (0.12 * (1 - dist / 12000)) + ")";
            ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(d.x, d.y); ctx.lineTo(e.x, e.y); ctx.stroke();
          }
        }
      }
      requestAnimationFrame(draw);
    }
    size(); draw();
    window.addEventListener("resize", size);
  }

  /* ---------- Service cards pre-select the enquiry form ---------- */
  var form = $("#enquiry");
  $$("[data-service]").forEach(function (card) {
    card.addEventListener("click", function () {
      if (form) form.service.value = card.dataset.service;
    });
  });
  $$("[data-focus-form]").forEach(function (b) {
    b.addEventListener("click", function (e) { e.preventDefault(); form.scrollIntoView({ behavior: "smooth", block: "center" }); setTimeout(function () { form.name.focus(); }, 600); });
  });

  /* ---------- Enquiry form -> WhatsApp ---------- */
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var ok = true;
      ["name", "phone"].forEach(function (f) {
        var el = form[f];
        el.classList.remove("is-invalid");
        if (!el.value.trim()) { void el.offsetWidth; el.classList.add("is-invalid"); ok = false; }
      });
      if (!ok) return;
      var msg = "Assalam o Alaikum ISB Domestic Staff,\n" +
        "Name: " + form.name.value.trim() + "\n" +
        "Phone: " + form.phone.value.trim() + "\n" +
        "Staff required: " + form.service.value;
      window.open("https://wa.me/" + WHATSAPP + "?text=" + encodeURIComponent(msg), "_blank", "noopener");
    });
  }

  var yr = $("#year"); if (yr) yr.textContent = new Date().getFullYear();
})();
