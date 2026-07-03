/**
 * Back-to-top button.
 *
 * Shows the button once the page has scrolled past SCROLL_THRESHOLD, and
 * scrolls smoothly back to the top on click (instantly if the user prefers
 * reduced motion).
 */
(function () {
  const button = document.getElementById("back-to-top");
  if (!button) return;

  const SCROLL_THRESHOLD = 120;

  /** Toggle the button's visible class based on the current scroll position. */
  const toggleVisibility = () => {
    button.classList.toggle("visible", window.scrollY > SCROLL_THRESHOLD);
  };

  window.addEventListener("scroll", toggleVisibility, { passive: true });
  toggleVisibility();

  button.addEventListener("click", () => {
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
  });
})();

/**
 * Scroll-reveal animation.
 *
 * Post cards (already marked with .reveal server-side) and every top-level
 * block inside an article's content fade + slide in the first time they
 * enter the viewport. Degrades to "everything visible" when JS can't
 * animate reliably (no IntersectionObserver support or reduced-motion
 * preference) — see the paired CSS rule gated on the has-js class for the
 * no-JS fallback.
 */
(function () {
  document.querySelectorAll(".post-content > *").forEach((el) => {
    el.classList.add("reveal");
  });

  const revealEls = document.querySelectorAll(".reveal");
  if (!revealEls.length) return;

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduceMotion || !("IntersectionObserver" in window)) {
    revealEls.forEach((el) => el.classList.add("in-view"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");
          // Reveal is one-shot: stop watching once an element has appeared.
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1, rootMargin: "0px 0px -60px 0px" }
  );

  revealEls.forEach((el) => observer.observe(el));
})();

/**
 * Dark/light mode toggle.
 *
 * Clicking the button sets an explicit data-theme attribute (persisted in
 * localStorage), which overrides the system prefers-color-scheme setting.
 * The stored preference is also applied synchronously from an inline
 * <head> script (see base.html) so there's no flash of the wrong theme on
 * load; this block only needs to handle the click and keep the button's
 * aria-label in sync with the current effective theme.
 */
(function () {
  const toggle = document.getElementById("theme-toggle");
  if (!toggle) return;

  const root = document.documentElement;
  const media = window.matchMedia("(prefers-color-scheme: dark)");

  /** True if the effective theme (explicit override or system) is dark. */
  const isDark = () => {
    const explicit = root.getAttribute("data-theme");
    return explicit ? explicit === "dark" : media.matches;
  };

  /** Keep the button's accessible name describing the action it performs. */
  const updateLabel = () => {
    toggle.setAttribute(
      "aria-label",
      isDark() ? "Activer le mode clair" : "Activer le mode sombre"
    );
  };

  updateLabel();
  // Keep the label accurate if the OS theme changes while no manual
  // override has been set (the CSS media query already repaints on its own).
  media.addEventListener("change", updateLabel);

  toggle.addEventListener("click", () => {
    const next = isDark() ? "light" : "dark";
    root.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
    updateLabel();
  });
})();
