(() => {
  function stack() {
    return document.getElementById("notification-stack");
  }

  function dismiss(toast) {
    if (!toast || toast.classList.contains("is-leaving")) return;
    toast.classList.add("is-leaving");
    setTimeout(() => toast.remove(), 190);
  }

  function arm(toast, timeout = 6000) {
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
    title.textContent = level === "error" ? "ERREUR / ERROR" : level === "warning" ? "ATTENTION / WARNING" : "SYSTÈME / SYSTEM";
    const close = document.createElement("button");
    close.type = "button";
    close.dataset.toastClose = "";
    close.setAttribute("aria-label", "Close");
    close.textContent = "×";
    head.append(title, close);

    const text = document.createElement("p");
    text.textContent = message;
    toast.append(head, text);
    root.appendChild(toast);
    arm(toast, timeout);
  }

  window.SomRPGNotify = notify;

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-toast]").forEach((toast) => arm(toast, 7000));
  });

  let lastUnexpected = 0;
  function unexpected() {
    const now = Date.now();
    if (now - lastUnexpected < 5000) return;
    lastUnexpected = now;
    notify("Erreur inattendue / Unexpected error. Vous pouvez continuer à jouer ou réessayer l'action.", "error", 8000);
  }

  window.addEventListener("error", unexpected);
  window.addEventListener("unhandledrejection", unexpected);
})();
