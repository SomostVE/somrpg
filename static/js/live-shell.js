(() => {
  const body = document.body;
  if (!body) return;

  const versionUrl = body.dataset.versionUrl;
  const chatUrl = body.dataset.chatUrl;
  const currentVersion = body.dataset.appVersion || "";
  const parisClock = document.getElementById("paris-clock");
  const resetCountdown = document.getElementById("reset-countdown");
  const versionBanner = document.getElementById("version-update-banner");
  let nextResetMs = null;
  let reloading = false;

  const parisFormatter = new Intl.DateTimeFormat("fr-FR", {
    timeZone: "Europe/Paris",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });

  function formatCountdown(milliseconds) {
    const total = Math.max(0, Math.floor(milliseconds / 1000));
    const hours = String(Math.floor(total / 3600)).padStart(2, "0");
    const minutes = String(Math.floor((total % 3600) / 60)).padStart(2, "0");
    const seconds = String(total % 60).padStart(2, "0");
    return `${hours}:${minutes}:${seconds}`;
  }

  function tickClock() {
    if (parisClock) parisClock.textContent = parisFormatter.format(new Date());
    if (resetCountdown && nextResetMs) resetCountdown.textContent = formatCountdown(nextResetMs - Date.now());
  }

  async function syncVersionAndReset() {
    if (!versionUrl) return;
    try {
      const response = await fetch(`${versionUrl}?t=${Date.now()}`, { cache: "no-store", credentials: "same-origin" });
      if (!response.ok) return;
      const data = await response.json();
      if (data.next_reset) nextResetMs = new Date(data.next_reset).getTime();
      if (data.version && currentVersion && data.version !== currentVersion && !reloading) {
        reloading = true;
        if (versionBanner) versionBanner.hidden = false;
        setTimeout(() => window.location.reload(), 900);
      }
    } catch (_) {
      // Deployment/restart window: retry on the next interval.
    }
  }

  function currentLanguage() {
    return document.documentElement.lang === "fr" ? "fr" : "en";
  }

  const chatMessages = document.getElementById("live-chat-messages");
  const chatForm = document.getElementById("live-chat-form");
  const chatInput = document.getElementById("live-chat-input");
  let chatSince = 0;
  let chatStarted = false;
  let chatPolling = false;

  function updateChatLanguage() {
    if (!chatInput) return;
    chatInput.placeholder = currentLanguage() === "fr" ? "Message (220 caractères max)" : "Message (220 characters max)";
    const empty = chatMessages?.querySelector(".chat-empty");
    if (empty) empty.textContent = currentLanguage() === "fr" ? "Aucun message reçu pendant cette connexion." : "No messages received during this connection.";
  }

  function ensureEmptyChat() {
    if (!chatMessages || chatMessages.children.length) return;
    const p = document.createElement("p");
    p.className = "chat-empty";
    p.textContent = currentLanguage() === "fr" ? "Aucun message reçu pendant cette connexion." : "No messages received during this connection.";
    chatMessages.appendChild(p);
  }

  function appendChatMessage(message) {
    if (!chatMessages) return;
    chatMessages.querySelector(".chat-empty")?.remove();
    const line = document.createElement("p");
    line.className = "chat-line";

    const time = document.createElement("time");
    time.textContent = parisFormatter.format(new Date(Number(message.time) * 1000));
    const name = document.createElement("strong");
    name.textContent = message.name || "Player";
    const text = document.createElement("span");
    text.textContent = message.text || "";

    line.append(time, name, text);
    chatMessages.appendChild(line);
    while (chatMessages.children.length > 80) chatMessages.firstElementChild?.remove();
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  async function pollChat(fresh = false) {
    if (!chatMessages || !chatUrl || chatPolling) return;
    chatPolling = true;
    try {
      const query = new URLSearchParams({ since: String(chatSince), fresh: fresh ? "1" : "0", t: String(Date.now()) });
      const response = await fetch(`${chatUrl}?${query}`, { cache: "no-store", credentials: "same-origin" });
      if (response.status === 403) return;
      if (!response.ok) return;
      const data = await response.json();
      if (fresh) {
        chatMessages.replaceChildren();
        chatStarted = true;
      }
      (data.messages || []).forEach(appendChatMessage);
      chatSince = Number(data.now || chatSince || Date.now() / 1000);
      ensureEmptyChat();
    } catch (_) {
      // Live chat is optional; retry silently.
    } finally {
      chatPolling = false;
    }
  }

  async function submitChat(event) {
    event.preventDefault();
    if (!chatForm || !chatInput || !chatInput.value.trim()) return;
    const button = chatForm.querySelector("button[type='submit']");
    if (button) button.disabled = true;
    try {
      const response = await fetch(chatUrl, {
        method: "POST",
        body: new FormData(chatForm),
        credentials: "same-origin",
        cache: "no-store",
      });
      if (response.ok) {
        chatInput.value = "";
        await pollChat(false);
      }
    } catch (_) {
      // Keep the typed message if sending failed.
    } finally {
      if (button) button.disabled = false;
      chatInput.focus();
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    tickClock();
    syncVersionAndReset();
    updateChatLanguage();

    if (chatForm && chatMessages) {
      chatForm.addEventListener("submit", submitChat);
      pollChat(true);
      setInterval(() => pollChat(false), 1500);
    }

    new MutationObserver(updateChatLanguage).observe(document.documentElement, { attributes: true, attributeFilter: ["lang"] });
  });

  setInterval(tickClock, 1000);
  setInterval(syncVersionAndReset, 30000);
})();
