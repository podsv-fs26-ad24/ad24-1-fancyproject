/* Story page: fixed right-gap wave (scroll-scrubbed) + left section nav */
(function () {
  let waveState = null;

  /** Voice-like amplitude (syllables, pauses, micro-jitter). */
  function voiceAmplitudeAt(t) {
    const phrase = 0.35 + 0.65 * Math.abs(Math.sin(t * Math.PI * 5.5 + 0.3));
    const syllable = Math.abs(Math.sin(t * Math.PI * 118 + 0.7));
    const flutter = Math.abs(Math.sin(t * Math.PI * 267 + 2.1)) * 0.42;
    const pause = Math.pow(Math.sin(t * Math.PI * 3.8 + 0.5), 6);
    const breath =
      Math.exp(-Math.pow((t - 0.08) * 11, 2)) * 0.35 +
      Math.exp(-Math.pow((t - 0.28) * 10, 2)) * 0.55 +
      Math.exp(-Math.pow((t - 0.52) * 9, 2)) * 0.48 +
      Math.exp(-Math.pow((t - 0.74) * 10, 2)) * 0.5 +
      Math.exp(-Math.pow((t - 0.92) * 12, 2)) * 0.4;
    const raw =
      phrase * (syllable * 0.58 + flutter * 0.42) * (1 - pause * 0.82) + breath * 0.45;
    return Math.max(0.1, Math.min(1, raw * 0.92 + 0.08));
  }

  function mountStoryChrome() {
    const rail = document.getElementById("story-spine-rail");
    if (rail && rail.parentElement !== document.body) {
      document.body.appendChild(rail);
    }
  }

  function docScrollHeight() {
    return Math.max(
      document.documentElement.scrollHeight,
      document.body.scrollHeight
    );
  }

  function drawFullWave(canvas, cssW, cssH) {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(cssW * dpr);
    canvas.height = Math.round(cssH * dpr);
    canvas.style.width = cssW + "px";
    canvas.style.height = cssH + "px";

    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, cssW, cssH);

    const grad = ctx.createLinearGradient(0, 0, 0, cssH);
    grad.addColorStop(0, "#b794f6");
    grad.addColorStop(0.28, "#6c8ef5");
    grad.addColorStop(0.55, "#56cfe1");
    grad.addColorStop(0.78, "#3ecf8e");
    grad.addColorStop(1, "#1ed760");
    ctx.fillStyle = grad;

    const cx = cssW / 2;
    const maxHalf = cssW * 0.46;
    const rows = Math.max(280, Math.min(720, Math.round(cssH / 1.65)));
    const rowH = cssH / rows;
    const stripe = Math.max(1, rowH * 0.92);

    for (let i = 0; i < rows; i++) {
      const t = i / Math.max(1, rows - 1);
      const amp = voiceAmplitudeAt(t);
      const wobble = Math.sin(t * Math.PI * 340 + 0.4) * cssW * 0.04 * amp;
      const half = amp * maxHalf;
      const y = i * rowH;
      const x0 = cx - half + wobble;
      const w = Math.max(1.5, half * 2 - Math.abs(wobble) * 0.5);
      ctx.globalAlpha = 0.55 + amp * 0.45;
      ctx.fillRect(x0, y, w, stripe);
    }
    ctx.globalAlpha = 1;
  }

  function updateWaveOffset() {
    if (!waveState) return;
    const { canvas, viewportH, waveH } = waveState;
    const maxScroll = docScrollHeight() - window.innerHeight;
    const pct = maxScroll > 0 ? window.scrollY / maxScroll : 0;
    const travel = Math.max(0, waveH - viewportH);
    canvas.style.transform = "translate3d(0," + -pct * travel + "px,0)";
  }

  function buildWave() {
    const rail = document.getElementById("story-spine-rail");
    const gap = document.getElementById("story-wave-gap");
    const canvas = document.getElementById("story-wave-gap-canvas");
    const viewport = gap && gap.querySelector(".story-wave-gap__viewport");
    if (!rail || !gap || !canvas || !viewport) return;

    const cssW = Math.max(48, gap.getBoundingClientRect().width || gap.clientWidth || 60);
    const viewportH = viewport.clientHeight || window.innerHeight - 60;
    const scrollH = docScrollHeight();
    const waveH = Math.max(scrollH, viewportH * 1.35);

    drawFullWave(canvas, cssW, waveH);
    waveState = { canvas, viewportH, waveH, gap };
    updateWaveOffset();
  }

  function initWaveGap() {
    const gap = document.getElementById("story-wave-gap");
    if (!gap) return;

    const mq = window.matchMedia("(min-width: 1024px)");

    const refresh = () => {
      if (!mq.matches) {
        waveState = null;
        return;
      }
      buildWave();
    };

    refresh();
    mq.addEventListener("change", refresh);
    window.addEventListener("resize", refresh, { passive: true });
    window.addEventListener("scroll", updateWaveOffset, { passive: true });

    if ("ResizeObserver" in window) {
      const ro = new ResizeObserver(refresh);
      ro.observe(document.documentElement);
      const rail = document.getElementById("story-spine-rail");
      if (rail) ro.observe(rail);
    }

    [50, 300, 900, 2000, 4000].forEach((ms) => setTimeout(refresh, ms));
  }

  function initStorySpine() {
    const rail = document.getElementById("story-spine-rail");
    const spine = document.getElementById("story-spine");
    const links = spine ? Array.from(spine.querySelectorAll(".story-spine__link")) : [];
    if (!rail || !spine || !links.length) return;

    const sections = links
      .map((link) => {
        const id = link.getAttribute("href").slice(1);
        return { link, el: document.getElementById(id) };
      })
      .filter((x) => x.el);

    const layoutLinks = () => {
      const maxScroll = docScrollHeight() - window.innerHeight;
      const navH = rail.clientHeight;
      const pad = Math.max(28, navH * 0.04);
      const usable = navH - pad * 2;

      sections.forEach(({ link, el }, i) => {
        let pct =
          maxScroll > 0 ? el.offsetTop / maxScroll : i / (sections.length - 1);
        pct = Math.max(0, Math.min(1, pct));
        link.style.top = pad + pct * usable + "px";
      });
    };

    const updateActive = () => {
      const y = window.scrollY + window.innerHeight * 0.28;
      let current = sections[0];
      sections.forEach((item) => {
        if (item.el.offsetTop <= y) current = item;
      });

      links.forEach((link) => link.classList.remove("is-active", "is-passed"));
      sections.forEach((item) => {
        if (item === current) item.link.classList.add("is-active");
        else if (item.el.offsetTop < y - 40) item.link.classList.add("is-passed");
      });
    };

    links.forEach((link) => {
      link.addEventListener("click", (e) => {
        const id = link.getAttribute("href").slice(1);
        const target = document.getElementById(id);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      });
    });

    const refresh = () => {
      layoutLinks();
      updateActive();
    };

    refresh();
    window.addEventListener("scroll", updateActive, { passive: true });
    window.addEventListener("resize", refresh, { passive: true });
    if ("ResizeObserver" in window) {
      new ResizeObserver(refresh).observe(rail);
    }
    [400, 1200, 2800].forEach((ms) => setTimeout(refresh, ms));
  }

  function initMobileJumpNav() {
    const links = document.querySelectorAll(
      ".story-jump-nav--mobile a[href^='#']"
    );
    if (!links.length) return;

    const items = [];
    links.forEach((link) => {
      const id = link.getAttribute("href").slice(1);
      const section = document.getElementById(id);
      if (section) items.push({ link, section });
    });

    const update = () => {
      const y = window.scrollY + 120;
      let current = items[0];
      items.forEach((item) => {
        if (item.section.offsetTop <= y) current = item;
      });
      links.forEach((l) => l.classList.remove("is-active"));
      if (current) current.link.classList.add("is-active");
    };

    links.forEach((link) => {
      link.addEventListener("click", (e) => {
        const id = link.getAttribute("href").slice(1);
        const target = document.getElementById(id);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      });
    });
    window.addEventListener("scroll", update, { passive: true });
    update();
  }

  function init() {
    if (!document.body.classList.contains("story-page")) return;

    mountStoryChrome();
    initWaveGap();
    initStorySpine();
    initMobileJumpNav();

    const sections = document.querySelectorAll("main section.level2");
    sections.forEach((el) => el.classList.add("story-reveal"));

    const hero = document.getElementById("title-block-header");
    if (hero) hero.classList.add("story-reveal", "is-visible");

    const figW = () => {
      const v = getComputedStyle(document.body)
        .getPropertyValue("--figure-width")
        .trim();
      const n = parseInt(v, 10);
      return Number.isFinite(n) ? n : 720;
    };

    const centerStoryViz = () => {
      const w = figW();
      document.querySelectorAll("body.story-page .story-viz-rail").forEach((r) => {
        r.style.display = "grid";
        r.style.justifyItems = "center";
        r.style.width = "min(" + w + "px, 100%)";
        r.style.maxWidth = w + "px";
        r.style.marginInline = "auto";
      });
      document.querySelectorAll("body.story-page .bk-root").forEach((root) => {
        const r = root.closest(".story-viz-rail");
        const targetW = r ? Math.min(w, r.clientWidth || w) : w;
        root.style.display = "block";
        root.style.marginLeft = "auto";
        root.style.marginRight = "auto";
        root.style.maxWidth = targetW + "px";
        root.style.width = targetW + "px";
        root.style.overflow = "visible";
        root.style.overflowX = "visible";
      });
      document.querySelectorAll("body.story-page section.level2 > hr").forEach((hr) => {
        hr.style.display = "block";
        hr.style.width = "min(" + w + "px, 100%)";
        hr.style.maxWidth = w + "px";
        hr.style.marginLeft = "auto";
        hr.style.marginRight = "auto";
      });
    };

    centerStoryViz();
    [100, 400, 1200, 2500].forEach((ms) => setTimeout(centerStoryViz, ms));
    document.addEventListener("bokeh:loaded", () => {
      centerStoryViz();
      if (waveState) buildWave();
    });
    window.addEventListener("resize", centerStoryViz, { passive: true });

    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add("is-visible");
              observer.unobserve(entry.target);
            }
          });
        },
        { root: null, rootMargin: "0px 0px -8% 0px", threshold: 0.12 }
      );
      sections.forEach((el) => observer.observe(el));
    } else {
      sections.forEach((el) => el.classList.add("is-visible"));
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
