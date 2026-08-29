"use strict";

(() => {
  const COOKIE_NAME = "zemazap_theme";
  const STORAGE_KEY = "zemazap_theme";

  const readTheme = () => {
    const match = document.cookie.match(
      new RegExp(`(?:^|;\\s*)${COOKIE_NAME}=(light|dark)(?:;|$)`),
    );
    if (match) return match[1];
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  };

  const updateControls = (theme) => {
    const nextIsDark = theme !== "dark";
    const label = nextIsDark ? "Включить тёмную тему" : "Включить светлую тему";
    document.querySelectorAll("[data-theme-toggle]").forEach((control) => {
      control.setAttribute("aria-label", label);
      control.setAttribute("title", label);
      control.querySelectorAll("[data-theme-label]").forEach((text) => {
        text.textContent = theme === "dark" ? "Светлая" : "Тёмная";
      });
    });
  };

  const applyTheme = (theme, persist = false) => {
    const normalizedTheme = theme === "dark" ? "dark" : "light";
    document.documentElement.dataset.theme = normalizedTheme;
    document.documentElement.style.colorScheme = normalizedTheme;

    if (persist) {
      const secure = window.location.protocol === "https:" ? "; Secure" : "";
      document.cookie = `${COOKIE_NAME}=${normalizedTheme}; Max-Age=31536000; Path=/; SameSite=Lax${secure}`;
      try {
        window.localStorage.setItem(STORAGE_KEY, normalizedTheme);
      } catch (_error) {
        // Cookies remain the cross-application source of truth.
      }
    }

    updateControls(normalizedTheme);
    window.dispatchEvent(new CustomEvent("zemazap-theme-change", { detail: normalizedTheme }));
  };

  applyTheme(readTheme());

  document.addEventListener("DOMContentLoaded", () => {
    updateControls(readTheme());
    document.querySelectorAll("[data-theme-toggle]").forEach((control) => {
      control.addEventListener("click", () => {
        applyTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark", true);
      });
    });
  });

  window.addEventListener("storage", (event) => {
    if (event.key === STORAGE_KEY && (event.newValue === "light" || event.newValue === "dark")) {
      applyTheme(event.newValue);
    }
  });
})();
