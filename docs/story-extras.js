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

  function styleBokehTooltips(root) {
    const scope = root || document;
    const tooltipVars = {
      "--background-color": "#1e1e2c",
      "--color": "#f4f4f8",
      "--divider-color": "#2e2e42",
      "--icon-color": "#2e2e42",
      "--tooltip-arrow-color": "#1e1e2c",
      "--tooltip-color": "#1e1e2c",
      "--tooltip-text": "#f4f4f8",
      "--tooltip-border": "#2e2e42",
      "--font-size": "0.84rem",
    };

    const shadowCss = `
      :host {
        --background-color: #1e1e2c !important;
        --color: #f4f4f8 !important;
        --divider-color: #2e2e42 !important;
        --icon-color: #2e2e42 !important;
        --tooltip-arrow-color: #1e1e2c !important;
        --tooltip-color: #1e1e2c !important;
        --tooltip-text: #f4f4f8 !important;
        --tooltip-border: #2e2e42 !important;
        background-color: rgba(30, 30, 44, 0.96) !important;
        color: #f4f4f8 !important;
        border-color: #2e2e42 !important;
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.55) !important;
        font-family: Figtree, system-ui, sans-serif !important;
        max-width: 280px !important;
      }
      .bk-tooltip-content {
        color: #f4f4f8 !important;
      }
      .bk-tooltip-row-label {
        color: #9ca3b8 !important;
      }
      .bk-tooltip-row-value {
        color: #f4f4f8 !important;
        font-weight: 600 !important;
      }
      .bk-tooltip-content > div:not(:first-child) {
        border-top-color: #2e2e42 !important;
      }
    `;

    scope.querySelectorAll('[popover="manual"]').forEach((host) => {
      Object.entries(tooltipVars).forEach(([key, value]) => {
        host.style.setProperty(key, value);
      });

      const shadow = host.shadowRoot;
      if (!shadow) return;
      if (!shadow.querySelector("[data-story-tooltip-dark]")) {
        const style = document.createElement("style");
        style.setAttribute("data-story-tooltip-dark", "1");
        style.textContent = shadowCss;
        shadow.appendChild(style);
      }
    });
  }

  function styleMoodMapLegend(root) {
    const scope = root || document;
    const legendCss = `
      .bk-panel.below,
      .bk-panel-above,
      .bk-panel-below {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
      }
      .bk-legend,
      .bk-legend-wrap {
        margin-inline: auto !important;
        width: fit-content !important;
        max-width: 100% !important;
        display: flex !important;
        flex-wrap: wrap !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 0.35rem 0.85rem !important;
      }
    `;

    scope
      .querySelectorAll(
        "body.story-page #sec-moodmap .bk-root, body.story-page .story-figure-sec5 .bk-root"
      )
      .forEach((host) => {
        const shadow = host.shadowRoot;
        if (!shadow || shadow.querySelector("[data-story-mood-legend]")) return;
        const style = document.createElement("style");
        style.setAttribute("data-story-mood-legend", "1");
        style.textContent = legendCss;
        shadow.appendChild(style);
      });
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
    const maxHalf = cssW * 0.48;
    const bars = Math.max(320, Math.min(760, Math.round(cssH / 2.5)));
    const stepY = cssH / Math.max(1, bars - 1);
    const barThickness = Math.max(2.4, Math.min(6.8, stepY * 0.62));

    // Subtle center line.
    ctx.globalAlpha = 0.32;
    ctx.strokeStyle = "#8df3df";
    ctx.lineWidth = Math.max(1, cssW * 0.022);
    ctx.beginPath();
    ctx.moveTo(cx, 0);
    ctx.lineTo(cx, cssH);
    ctx.stroke();

    // Voice-wave style: thin baseline + quiet stretches + clustered bursts.
    ctx.globalAlpha = 0.95;
    ctx.strokeStyle = grad;
    ctx.lineCap = "round";
    ctx.lineWidth = barThickness;
    const peakEnvelope = (t) => (
      Math.exp(-Math.pow((t - 0.16) * 20, 2)) * 1.0 +
      Math.exp(-Math.pow((t - 0.30) * 14, 2)) * 0.45 +
      Math.exp(-Math.pow((t - 0.57) * 18, 2)) * 0.88 +
      Math.exp(-Math.pow((t - 0.74) * 13, 2)) * 0.42
    );

    const noise = (i) => {
      // Deterministic pseudo-random jitter, stable across renders.
      const x = Math.sin((i + 13) * 12.9898) * 43758.5453;
      return x - Math.floor(x);
    };

    for (let i = 0; i < bars; i++) {
      const t = i / Math.max(1, bars - 1);
      const y = i * stepY;
      const env = Math.min(1, peakEnvelope(t) + voiceAmplitudeAt(t) * 0.08);
      const carrier =
        0.62 * Math.abs(Math.sin(t * Math.PI * 58 + 0.35)) +
        0.25 * Math.abs(Math.sin(t * Math.PI * 27 + 1.2)) +
        0.13 * Math.abs(Math.sin(t * Math.PI * 7 + 2.3));
      const jitter = 0.84 + noise(i) * 0.28;
      const amp = Math.max(0.006, Math.min(1, env * (0.18 + carrier * 0.86) * jitter));
      const half = Math.max(0.75, maxHalf * amp);
      const edgeFade = 0.72 + 0.28 * Math.sin(Math.PI * t);
      ctx.globalAlpha = 0.55 + 0.4 * edgeFade;
      ctx.beginPath();
      ctx.moveTo(cx - half, y);
      ctx.lineTo(cx + half, y);
      ctx.stroke();
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
      return Number.isFinite(n) ? n : 640;
    };

    const centerStoryViz = () => {
      const w = figW();
      document.querySelectorAll("body.story-page .story-viz-rail").forEach((r) => {
        r.style.display = "grid";
        r.style.justifyItems = "stretch";
        r.style.width = "100%";
        r.style.maxWidth = "100%";
        r.style.marginInline = "0";
      });
      document.querySelectorAll("body.story-page .bk-root").forEach((root) => {
        root.style.display = "block";
        root.style.marginLeft = "0";
        root.style.marginRight = "0";
        root.style.maxWidth = "100%";
        root.style.width = "100%";
        root.style.boxSizing = "border-box";
        root.style.overflow = "visible";
        root.style.overflowX = "auto";
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
      styleBokehTooltips();
      styleMoodMapLegend();
      if (waveState) buildWave();
    });
    window.addEventListener("resize", centerStoryViz, { passive: true });

    styleBokehTooltips();
    styleMoodMapLegend();
    [100, 400, 1200, 2500].forEach((ms) => {
      setTimeout(() => {
        styleBokehTooltips();
        styleMoodMapLegend();
      }, ms);
    });
    if ("MutationObserver" in window) {
      const tooltipObserver = new MutationObserver(() => {
        styleBokehTooltips();
        styleMoodMapLegend();
      });
      tooltipObserver.observe(document.body, { childList: true, subtree: true });
    }
    document.addEventListener("pointermove", () => styleBokehTooltips(), { passive: true });

    document.querySelectorAll('a[href^="#sec-"]').forEach((link) => {
      link.addEventListener("click", (event) => {
        const id = link.getAttribute("href");
        if (!id || id.length < 2) return;
        const target = document.querySelector(id);
        if (!target) return;
        event.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
        if (history.replaceState) {
          history.replaceState(null, "", id);
        }
      });
    });

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
