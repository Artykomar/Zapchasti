export const themeCookieName = "zemazap_theme";
export const themeStorageKey = "zemazap_theme";

export type ZemazapTheme = "light" | "dark";

export const themeInitializationScript = `(() => {
  const match = document.cookie.match(/(?:^|;\\s*)${themeCookieName}=(light|dark)(?:;|$)/);
  const theme = match ? match[1] : (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  document.documentElement.dataset.theme = theme;
  document.documentElement.style.colorScheme = theme;
})();`;
