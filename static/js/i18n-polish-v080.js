(() => {
  const originalTitles = new Map();
  const titleRules = [
    [/^Shop - SomRPG$/i, "Boutique - SomRPG"],
    [/^Tower - SomRPG$/i, "Tour - SomRPG"],
    [/^Camp - SomRPG$/i, "Camp - SomRPG"],
    [/^Character Record - SomRPG$/i, "Dossier du personnage - SomRPG"],
    [/^Inventory - SomRPG$/i, "Inventaire - SomRPG"],
    [/^City Guard - SomRPG$/i, "Garde de la ville - SomRPG"],
    [/^Workshop - SomRPG$/i, "Atelier - SomRPG"],
    [/^Community - SomRPG$/i, "Communauté - SomRPG"],
    [/^Content Index - SomRPG$/i, "Index du contenu - SomRPG"],
    [/^New Record - SomRPG$/i, "Nouveau dossier - SomRPG"],
    [/^Town - SomRPG$/i, "Ville - SomRPG"],
    [/^Floor (\d+) - SomRPG$/i, "Étage $1 - SomRPG"],
  ];

  function frenchTitle(value) {
    for (const [pattern, replacement] of titleRules) {
      if (pattern.test(value)) return value.replace(pattern, replacement);
    }
    return value;
  }

  function sync() {
    const french = document.documentElement.lang === "fr";
    if (!originalTitles.has(document, "title")) originalTitles.set(document, document.title);
    const originalTitle = originalTitles.get(document) || document.title;
    document.title = french ? frenchTitle(originalTitle) : originalTitle;

    document.querySelectorAll('[aria-label="Main commands"], [aria-label="Language / Langue"]').forEach((element) => {
      const original = element.dataset.i18nOriginalAria || element.getAttribute("aria-label") || "";
      if (!element.dataset.i18nOriginalAria) element.dataset.i18nOriginalAria = original;
      if (!french) {
        element.setAttribute("aria-label", original);
      } else if (original === "Main commands") {
        element.setAttribute("aria-label", "Commandes principales");
      } else if (original === "Language / Langue") {
        element.setAttribute("aria-label", "Langue");
      }
    });
  }

  document.addEventListener("DOMContentLoaded", sync);
  new MutationObserver(sync).observe(document.documentElement, { attributes: true, attributeFilter: ["lang"] });
})();
