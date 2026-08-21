(() => {
  function currentLanguage() {
    return document.documentElement.lang === "fr" ? "fr" : "en";
  }

  function stack() {
    return document.getElementById("notification-stack");
  }

  function toastLevel(toast) {
    if (toast.classList.contains("toast-error")) return "error";
    if (toast.classList.contains("toast-warning")) return "warning";
    if (toast.classList.contains("toast-success")) return "success";
    return "info";
  }

  function titleFor(level) {
    const fr = currentLanguage() === "fr";
    if (level === "error") return fr ? "ERREUR" : "ERROR";
    if (level === "warning") return fr ? "ATTENTION" : "WARNING";
    return fr ? "SYSTÈME" : "SYSTEM";
  }

  function localizeToast(toast) {
    const title = toast?.querySelector(".system-toast-head strong");
    if (title) title.textContent = titleFor(toastLevel(toast));
    const close = toast?.querySelector("[data-toast-close]");
    if (close) close.setAttribute("aria-label", currentLanguage() === "fr" ? "Fermer" : "Close");
  }

  function dismiss(toast) {
    if (!toast || toast.classList.contains("is-leaving")) return;
    toast.classList.add("is-leaving");
    setTimeout(() => toast.remove(), 190);
  }

  function arm(toast, timeout = 6000) {
    localizeToast(toast);
    const close = toast.querySelector("[data-toast-close]");
    if (close) close.addEventListener("click", () => dismiss(toast));
    if (timeout > 0) setTimeout(() => dismiss(toast), timeout);
  }

  function notify(message, level = "error", timeout = 6500) {
    const root = stack();
    if (!root || !message) return;
    const toast = document.createElement("div");
    toast.className = `system-toast toast-${level}`;
    toast.dataset.toast = "";

    const head = document.createElement("div");
    head.className = "system-toast-head";
    const title = document.createElement("strong");
    title.textContent = titleFor(level);
    const close = document.createElement("button");
    close.type = "button";
    close.dataset.toastClose = "";
    close.setAttribute("aria-label", currentLanguage() === "fr" ? "Fermer" : "Close");
    close.textContent = "×";
    head.append(title, close);

    const text = document.createElement("p");
    text.textContent = message;
    toast.append(head, text);
    root.appendChild(toast);
    arm(toast, timeout);
  }

  function markActiveMenu() {
    const here = window.location.pathname.replace(/\/+$/, "") || "/";
    document.querySelectorAll(".evolving-command .menu-entry").forEach((entry) => {
      let target = "/";
      try {
        target = new URL(entry.href, window.location.origin).pathname.replace(/\/+$/, "") || "/";
      } catch (_) {
        return;
      }
      const active = target === here;
      entry.classList.toggle("is-active", active);
      if (active) entry.setAttribute("aria-current", "page");
      else entry.removeAttribute("aria-current");
    });
  }

  window.SomRPGNotify = notify;

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-toast]").forEach((toast) => arm(toast, 7000));
    markActiveMenu();
    new MutationObserver(() => {
      document.querySelectorAll("[data-toast]").forEach(localizeToast);
    }).observe(document.documentElement, { attributes: true, attributeFilter: ["lang"] });
  });

  let lastUnexpected = 0;
  function unexpected() {
    const now = Date.now();
    if (now - lastUnexpected < 5000) return;
    lastUnexpected = now;
    notify(
      currentLanguage() === "fr"
        ? "Erreur inattendue. Vous pouvez continuer à jouer ou réessayer l'action."
        : "Unexpected error. You can keep playing or retry the action.",
      "error",
      8000,
    );
  }

  window.addEventListener("error", unexpected);
  window.addEventListener("unhandledrejection", unexpected);
})();
