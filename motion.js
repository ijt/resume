// Animation layer for motion.html. Without this script (or with reduced motion
// requested), the page is simply the static resume.
(() => {
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const root = document.documentElement;
  root.classList.add("js");

  // Split the name into letters that rise in one by one.
  const h1 = document.querySelector("h1");
  const name = h1.textContent;
  h1.textContent = "";
  h1.setAttribute("aria-label", name);
  [...name].forEach((c, i) => {
    if (c === " ") return h1.append(" ");
    const s = document.createElement("span");
    s.className = "ch";
    s.setAttribute("aria-hidden", "true");
    s.style.setProperty("--i", i);
    s.textContent = c;
    h1.append(s);
  });

  // Count numbers like "1,000+" and "50 ms" up from zero when they appear.
  const counters = new Map();
  for (const el of document.querySelectorAll("strong")) {
    const m = el.textContent.match(/^(\d[\d,]*)([\s\S]*)$/);
    if (!m) continue;
    el.classList.add("count");
    counters.set(el, { n: Number(m[1].replace(/,/g, "")), rest: m[2] });
  }
  const countUp = (el) => {
    const { n, rest } = counters.get(el);
    const t0 = performance.now();
    const tick = (t) => {
      const k = Math.min(1, (t - t0) / 1400);
      const v = Math.round(n * (1 - Math.pow(1 - k, 3)));
      el.textContent = v.toLocaleString("en-US") + rest;
      if (k < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };

  // Reveal elements as they scroll into view, staggering each batch.
  const targets = document.querySelectorAll(
    ".role, .contact, h2, .summary, .skills dt, .skills dd, .job-head, .sub, " +
    ".job li, .project, .compact li, .edu > div"
  );
  targets.forEach((el) => el.classList.add("reveal"));
  const io = new IntersectionObserver((entries) => {
    entries
      .filter((e) => e.isIntersecting)
      .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
      .forEach((e, i) => {
        const el = e.target;
        el.style.setProperty("--d", `${Math.min(i, 12) * 70}ms`);
        el.classList.add("in");
        io.unobserve(el);
        el.querySelectorAll("strong.count").forEach((s) =>
          setTimeout(() => countUp(s), 200 + i * 70)
        );
      });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.1 });
  targets.forEach((el) => io.observe(el));
  // Hold counters at zero until revealed.
  counters.forEach(({ rest }, el) => { el.textContent = "0" + rest; });

  // Reading progress bar and the experience timeline follow the scroll.
  const bar = document.createElement("div");
  bar.className = "progress";
  document.body.prepend(bar);
  const xp = [...document.querySelectorAll("section")]
    .find((s) => s.querySelector("h2")?.textContent === "Experience");
  xp?.classList.add("xp");
  const jobs = xp ? [...xp.querySelectorAll(".job")] : [];

  const onScroll = () => {
    const max = root.scrollHeight - innerHeight;
    bar.style.setProperty("--p", max > 0 ? scrollY / max : 1);
    if (!xp) return;
    const line = innerHeight * 0.6;
    const r = xp.getBoundingClientRect();
    xp.style.setProperty("--tl", Math.max(0, Math.min(1, (line - r.top) / r.height)));
    jobs.forEach((j) => j.classList.toggle("lit", j.getBoundingClientRect().top < line));
  };
  addEventListener("scroll", onScroll, { passive: true });
  addEventListener("resize", onScroll);
  onScroll();

  // A soft spotlight follows the pointer across the page.
  const page = document.querySelector(".page");
  page.addEventListener("pointermove", (e) => {
    const r = page.getBoundingClientRect();
    page.style.setProperty("--mx", `${e.clientX - r.left}px`);
    page.style.setProperty("--my", `${e.clientY - r.top}px`);
  });
})();
