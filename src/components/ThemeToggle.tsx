"use client";

import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";
import { themeCookieName, themeStorageKey, type ZemazapTheme } from "@/src/components/themePreference";

const currentTheme = (): ZemazapTheme =>
  document.documentElement.dataset.theme === "dark" ? "dark" : "light";

const applyTheme = (theme: ZemazapTheme) => {
  const secure = window.location.protocol === "https:" ? "; Secure" : "";
  document.documentElement.dataset.theme = theme;
  document.documentElement.style.colorScheme = theme;
  document.cookie = `${themeCookieName}=${theme}; Max-Age=31536000; Path=/; SameSite=Lax${secure}`;
  window.localStorage.setItem(themeStorageKey, theme);
  window.dispatchEvent(new CustomEvent("zemazap-theme-change", { detail: theme }));
};

export default function ThemeToggle() {
  const [theme, setTheme] = useState<ZemazapTheme>("light");

  useEffect(() => {
    const sync = () => setTheme(currentTheme());
    sync();
    window.addEventListener("zemazap-theme-change", sync);
    window.addEventListener("storage", sync);
    return () => {
      window.removeEventListener("zemazap-theme-change", sync);
      window.removeEventListener("storage", sync);
    };
  }, []);

  const nextTheme = theme === "dark" ? "light" : "dark";
  const label = nextTheme === "dark" ? "Включить тёмную тему" : "Включить светлую тему";

  return (
    <button
      className="theme-switch"
      type="button"
      aria-label={label}
      title={label}
      onClick={() => {
        applyTheme(nextTheme);
        setTheme(nextTheme);
      }}
    >
      {theme === "dark" ? <Sun size={18} aria-hidden="true" /> : <Moon size={18} aria-hidden="true" />}
      <span className="theme-switch__label">{theme === "dark" ? "Светлая" : "Тёмная"}</span>
    </button>
  );
}
