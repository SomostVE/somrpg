(() => {
  const originals = new WeakMap();
  const optionOriginals = new WeakMap();

  const rules = [
    [/^BOSS GATE: (.+) blocks Floor (\d+)\.$/, "PORTE DU BOSS : $1 bloque l'étage $2."],
    [/^Round (\d+): (.+) deals (\d+) damage\.$/, "Tour $1 : $2 inflige $3 dégâts."],
    [/^(.+) deals (\d+) damage\.$/, "$1 inflige $2 dégâts."],
    [/^End City Guard duty first\.$/, "Terminez d'abord le service de garde."],
    [/^Floor locked\.$/, "Étage verrouillé."],
    [/^Not enough gold\.$/, "Pas assez d'or."],
    [/^Purchased (.+)\.$/, "$1 acheté."],
    [/^This item is not equippable\.$/, "Cet objet ne peut pas être équipé."],
    [/^City Guard duty started\.$/, "Service de garde commencé."],
    [/^Already on duty\.$/, "Déjà en service."],
    [/^No active guard duty\.$/, "Aucun service de garde actif."],
    [/^Guard duty ended: \+(\d+) gold, \+(\d+) supplies\.$/, "Service terminé : +$1 or, +$2 ressources."],
    [/^No encounter configured here\.$/, "Aucune rencontre configurée ici."],
    [/^(.+) was defeated\.$/, "$1 a été vaincu."],
    [/^Not enough resources\.$/, "Pas assez de ressources."],
    [/^Crafted (.+)\.$/, "$1 fabriqué."],
    [/^Connected as (.+)\.$/, "Connecté en tant que $1."],
    [/^Discord account disconnected from this session\.$/, "Compte Discord déconnecté de cette session."],
  ];

  const optionTranslations = {
    Vanguard: "Avant-garde",
    Strider: "Éclaireur",
    Arcanist: "Arcaniste",
  };

  function toFrench(text) {
    for (const [pattern, replacement] of rules) {
      if (pattern.test(text)) return text.replace(pattern, replacement);
    }
    return text;
  }

  function apply() {
    const french = document.documentElement.lang === "fr";

    document.querySelectorAll(".system-message, .combat-log p").forEach((node) => {
      if (!originals.has(node)) originals.set(node, node.textContent);
      const original = originals.get(node);
      node.textContent = french ? toFrench(original) : original;
    });

    document.querySelectorAll("select option").forEach((option) => {
      if (!optionOriginals.has(option)) optionOriginals.set(option, option.textContent);
      const original = optionOriginals.get(option);
      option.textContent = french ? (optionTranslations[original] || original) : original;
    });
  }

  document.addEventListener("DOMContentLoaded", apply);
  new MutationObserver(apply).observe(document.documentElement, {attributes: true, attributeFilter: ["lang"]});
  new MutationObserver(apply).observe(document.body, {subtree: true, childList: true});
})();
