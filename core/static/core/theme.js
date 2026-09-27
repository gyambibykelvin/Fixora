(() => {
  const storageKey = "fixora-theme";
  const root = document.documentElement;

  function applyTheme(theme) {
    const isDark = theme === "dark";
    root.setAttribute("data-theme", isDark ? "dark" : "light");
    document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
      button.textContent = isDark ? "☀" : "☾";
      button.setAttribute(
        "aria-label",
        isDark ? "Switch to light mode" : "Switch to dark mode",
      );
      button.setAttribute("title", button.getAttribute("aria-label"));
    });
  }

  window.toggleFixoraTheme = () => {
    const nextTheme = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    localStorage.setItem(storageKey, nextTheme);
    applyTheme(nextTheme);
  };

  applyTheme(localStorage.getItem(storageKey) || "light");

  document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
    button.addEventListener("click", window.toggleFixoraTheme);
  });
})();
