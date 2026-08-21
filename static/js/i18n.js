(() => {
  const STORAGE_KEY = "somrpg.language";

  const fr = new Map(Object.entries({
    "DUNGEON ARCHIVE / COMMUNITY TERMINAL": "ARCHIVES DU DONJON / TERMINAL COMMUNAUTAIRE",
    "CONNECT DISCORD": "CONNECTER DISCORD",
    "LOCAL MODE": "MODE LOCAL",
    "CITY GUARD ACTIVE": "GARDE DE LA VILLE ACTIVE",
    "SAVE ACTIVE": "SAUVEGARDE ACTIVE",
    "NEW RECORD": "NOUVEAU DOSSIER",
    "STATUS": "STATUT",
    "SUPPLY": "RESSOURCES",
    "CRAFT XP": "XP ARTISANAT",
    "FLOOR": "ÉTAGE",
    "COMMAND": "COMMANDES",
    "Camp": "Camp",
    "Character": "Personnage",
    "Inventory": "Inventaire",
    "City Guard": "Garde de la ville",
    "Workshop": "Atelier",
    "Town": "Ville",
    "Codex": "Codex",
    "Community": "Communauté",
    "Explore": "Donjon",
    "[ON DUTY]": "[EN SERVICE]",
    "> Disconnect account": "> Déconnecter le compte",
    "SYSTEM LOG": "JOURNAL SYSTÈME",
    "NETWORK": "RÉSEAU",
    "> Open Community Rankings": "> Ouvrir les classements communautaires",
    "> Connect with Discord": "> Se connecter avec Discord",
    "SOMRPG TERMINAL": "TERMINAL SOMRPG",
    "DJANGO / SQLITE / DISCORD COMMUNITY": "DJANGO / SQLITE / COMMUNAUTÉ DISCORD",

    "CURRENT ASCENT // READY": "ASCENSION ACTUELLE // PRÊT",
    "LEVEL": "NIVEAU",
    "EXPERIENCE": "EXPÉRIENCE",
    "MAX HP": "PV MAX",
    "GOLD": "OR",
    "> Advance into the dungeon": "> Avancer dans le donjon",
    "CLEAR THE ENCOUNTER TO OPEN THE NEXT FLOOR.": "ÉLIMINEZ L'ENNEMI POUR OUVRIR L'ÉTAGE SUIVANT.",
    "CAMP NOTES": "NOTES DU CAMP",
    "Character displays permanent stats and equipment bonuses.": "Personnage affiche les statistiques permanentes et les bonus d'équipement.",
    "Inventory contains recovered items and equipment.": "Inventaire contient les objets récupérés et l'équipement.",
    "Explore starts the current floor encounter.": "Donjon lance le combat de l'étage actuel.",
    "Combat resolves automatically and is recorded line by line.": "Le combat se résout automatiquement et est enregistré ligne par ligne.",

    "CHARACTER RECORD": "DOSSIER DU PERSONNAGE",
    "GUILD FILE // ACTIVE ADVENTURER": "DOSSIER DE GUILDE // AVENTURIER ACTIF",
    "Current combat registration and progression record. Equipment modifiers are included in the final attack and defense values shown below.": "Dossier actuel de combat et de progression. Les modificateurs d'équipement sont inclus dans les valeurs finales d'attaque et de défense ci-dessous.",
    "BASE ATK": "ATQ BASE",
    "BASE DEF": "DEF BASE",
    "GEAR ATK": "ATQ ÉQUIPEMENT",
    "GEAR DEF": "DEF ÉQUIPEMENT",
    "TOTAL ATK": "ATQ TOTALE",
    "TOTAL DEF": "DEF TOTALE",
    "CURRENT FLOOR": "ÉTAGE ACTUEL",
    "PROGRESSION NOTES": "NOTES DE PROGRESSION",
    "Leveling increases maximum HP, attack and defense.": "Monter de niveau augmente les PV maximum, l'attaque et la défense.",
    "Equipped loot contributes passive combat bonuses.": "L'équipement porté apporte des bonus passifs en combat.",
    "More character systems will be added after the core dungeon loop is stable.": "D'autres systèmes de personnage seront ajoutés une fois la boucle principale du donjon stabilisée.",

    "INVENTORY CHEST": "COFFRE D'INVENTAIRE",
    "RECOVERED MATERIAL // EQUIPMENT": "MATÉRIEL RÉCUPÉRÉ // ÉQUIPEMENT",
    "Recovered objects are catalogued here. Equip useful pieces before advancing deeper into the dungeon.": "Les objets récupérés sont catalogués ici. Équipez les pièces utiles avant de descendre plus profondément dans le donjon.",
    "Unequip": "Retirer",
    "Equip": "Équiper",
    "[EMPTY] No recovered items are stored in the chest.": "[VIDE] Aucun objet récupéré n'est stocké dans le coffre.",
    "EQUIPMENT NOTES": "NOTES D'ÉQUIPEMENT",
    "Equipment currently grants passive attack or defense bonuses.": "L'équipement accorde actuellement des bonus passifs d'attaque ou de défense.",
    "Item rarity is indicated by the colored line on the left side of each record.": "La rareté d'un objet est indiquée par la ligne colorée à gauche de chaque fiche.",
    "Weapon, armor and accessory slots will be separated in a later build.": "Les emplacements d'arme, d'armure et d'accessoire seront séparés dans une version ultérieure.",
    "EQUIPPED": "ÉQUIPÉ",
    "COMMON": "COMMUN",
    "UNCOMMON": "PEU COMMUN",
    "RARE": "RARE",
    "EPIC": "ÉPIQUE",
    "LEGENDARY": "LÉGENDAIRE",
    "QTY": "QTÉ",

    "DUNGEON ENCOUNTER": "RENCONTRE DU DONJON",
    "HOSTILE SIGNAL DETECTED": "PRÉSENCE HOSTILE DÉTECTÉE",
    "ACTIVE THREAT": "MENACE ACTIVE",
    "A hostile presence blocks the route to the next floor. Battle resolution is automatic, but every exchange is recorded in the combat log.": "Une présence hostile bloque l'accès à l'étage suivant. Le combat est automatique, mais chaque échange est consigné dans le journal de combat.",
    "ENEMY HP": "PV ENNEMI",
    "ENEMY ATK": "ATQ ENNEMI",
    "ENEMY DEF": "DEF ENNEMI",
    "XP REWARD": "RÉCOMPENSE XP",
    "DROP": "BUTIN",
    "NONE": "AUCUN",
    "> Begin auto battle": "> Commencer le combat automatique",
    "THE ENCOUNTER WILL RESOLVE TURN BY TURN.": "LE COMBAT SE RÉSOUDRA TOUR PAR TOUR.",
    "COMBAT LOG": "JOURNAL DE COMBAT",
    "BATTLE RESULT": "RÉSULTAT DU COMBAT",
    "VICTORY CONFIRMED": "VICTOIRE CONFIRMÉE",
    "DEFEAT RECORDED": "DÉFAITE ENREGISTRÉE",
    "LOOT": "BUTIN",
    "LEVELS GAINED": "NIVEAUX GAGNÉS",
    "Check inventory": "Vérifier l'inventaire",
    "> Return to camp": "> Retourner au camp",

    "CITY GUARD / WESTERN GATE": "GARDE DE LA VILLE / PORTE OUEST",
    "AFK SERVICE": "SERVICE AFK",
    "ON DUTY": "EN SERVICE",
    "AVAILABLE": "DISPONIBLE",
    "City Guard": "Garde de la ville",
    "CURRENT SHIFT": "SERVICE ACTUEL",
    "GOLD IF ENDED NOW": "OR SI ARRÊT MAINTENANT",
    "SUPPLIES IF ENDED NOW": "RESSOURCES SI ARRÊT MAINTENANT",
    "LIFETIME SERVICE": "TEMPS TOTAL DE SERVICE",
    "> End guard duty and collect": "> Terminer le service et récupérer",
    "UNFINISHED REWARD PROGRESS IS KEPT FOR YOUR NEXT SHIFT. NO AFK TIME IS LOST.": "LA PROGRESSION INACHEVÉE EST CONSERVÉE POUR LE PROCHAIN SERVICE. AUCUN TEMPS AFK N'EST PERDU.",
    "The city always needs another pair of eyes on the walls. Start a shift before leaving the game and return whenever you want. Guard duty produces a small amount of gold and common supplies while you are away.": "La ville a toujours besoin de gardes supplémentaires sur les remparts. Commencez un service avant de quitter le jeu et revenez quand vous voulez. La garde produit un peu d'or et des ressources communes pendant votre absence.",
    "GOLD RATE": "TAUX D'OR",
    "SUPPLY RATE": "TAUX DE RESSOURCES",
    "SUPPLIES OWNED": "RESSOURCES POSSÉDÉES",
    "SHIFTS COMPLETED": "SERVICES TERMINÉS",
    "> Begin guard duty": "> Commencer le service",
    "NO DURATION TO CHOOSE. START NOW, STOP WHENEVER YOU RETURN.": "AUCUNE DURÉE À CHOISIR. COMMENCEZ MAINTENANT ET ARRÊTEZ À VOTRE RETOUR.",
    "SERVICE NOTES": "NOTES DE SERVICE",
    "Guard duty is intended for time when you are not actively playing.": "La garde est destinée aux périodes où vous ne jouez pas activement.",
    "Dungeon exploration is unavailable while a guard shift is active.": "L'exploration du donjon est indisponible pendant un service de garde.",
    "Stopping early never deletes partial progress toward the next reward.": "Arrêter tôt ne supprime jamais la progression partielle vers la prochaine récompense.",
    "Supplies are a generic resource for now and can later feed crafting and city systems.": "Les ressources sont génériques pour le moment et pourront ensuite alimenter l'artisanat et les systèmes de la ville.",

    "WORKSHOP": "ATELIER",
    "ARTISANAT // RANKING COEFFICIENT ×2": "ARTISANAT // COEFFICIENT DE CLASSEMENT ×2",
    "Crafting Bench": "Établi d'artisanat",
    "Crafting converts Guard supplies and gold into equipment. Every completed recipe grants Crafting XP, which feeds the community Artisanat ranking.": "L'artisanat transforme les ressources de la garde et l'or en équipement. Chaque recette terminée accorde de l'XP d'artisanat, utilisée pour le classement communautaire Artisanat.",
    "SUPPLIES": "RESSOURCES",
    "CRAFTING XP": "XP ARTISANAT",
    "RANK COEFFICIENT": "COEFFICIENT DE CLASSEMENT",
    "AVAILABLE RECIPES": "RECETTES DISPONIBLES",
    "> Craft": "> Fabriquer",
    "No recipe is available.": "Aucune recette n'est disponible.",
    "OUTPUT": "PRODUIT",

    "PASSIVE DISCOVERY // RANKING COEFFICIENT ×0.5": "DÉCOUVERTE PASSIVE // COEFFICIENT DE CLASSEMENT ×0,5",
    "Archive Completion": "Progression des archives",
    "The Codex fills itself while you play. Encounter enemies, recover loot, and craft new items; no separate grind is required.": "Le Codex se remplit automatiquement pendant que vous jouez. Rencontrez des ennemis, récupérez du butin et fabriquez de nouveaux objets ; aucun farm séparé n'est nécessaire.",
    "COMPLETION": "COMPLÉTION",
    "DISCOVERED": "DÉCOUVERT",
    "ENEMIES": "ENNEMIS",
    "ITEMS": "OBJETS",
    "BESTIARY": "BESTIAIRE",
    "ITEM ARCHIVE": "ARCHIVES DES OBJETS",
    "[FOUND]": "[TROUVÉ]",
    "No enemy has been catalogued yet.": "Aucun ennemi n'a encore été catalogué.",
    "No item has been catalogued yet.": "Aucun objet n'a encore été catalogué.",

    "COMMUNITY EVENT": "ÉVÉNEMENT COMMUNAUTAIRE",
    "NO ACTIVE SEASON": "AUCUNE SAISON ACTIVE",
    "Global Rankings": "Classement global",
    "Global points combine four independent rankings. Each activity is normalized to 100 points before coefficients are applied, so raw values from different systems remain comparable.": "Les points globaux combinent quatre classements indépendants. Chaque activité est normalisée sur 100 points avant application des coefficients afin que les valeurs de systèmes différents restent comparables.",
    "DUNGEON": "DONJON",
    "COMMERCE": "COMMERCE",
    "CRAFTING": "ARTISANAT",
    "Floors cleared": "Étages terminés",
    "Total gold earned": "Or total gagné",
    "Crafting XP earned": "XP d'artisanat gagnée",
    "Discovery completion": "Complétion des découvertes",
    "COMMUNITY ACCOUNT REQUIRED": "COMPTE COMMUNAUTAIRE REQUIS",
    "Connect with Discord to create a persistent community identity and enter seasonal rankings.": "Connectez-vous avec Discord pour créer une identité communautaire persistante et participer aux classements saisonniers.",
    "Discord OAuth is not configured on this server yet.": "Discord OAuth n'est pas encore configuré sur ce serveur.",
    "ACCOUNT CONNECTED": "COMPTE CONNECTÉ",
    "Your Discord identity is ready. Create a SomRPG character to enter the event.": "Votre identité Discord est prête. Créez un personnage SomRPG pour participer à l'événement.",
    "> Create character": "> Créer un personnage",
    "GLOBAL RANK": "RANG GLOBAL",
    "GLOBAL POINTS": "POINTS GLOBAUX",
    "SEASON STANDINGS": "CLASSEMENT DE LA SAISON",
    "PLAYER": "JOUEUR",
    "GLOBAL": "GLOBAL",
    "No ranked adventurer has joined this season yet.": "Aucun aventurier classé n'a encore rejoint cette saison.",

    "ADVENTURER REGISTRATION": "ENREGISTREMENT DE L'AVENTURIER",
    "NEW RECORD // FLOOR 01": "NOUVEAU DOSSIER // ÉTAGE 01",
    "Create your adventurer": "Créez votre aventurier",
    "The terminal hums to life. A blank guild record waits for a name. Beyond this screen lies a dungeon measured in floors, encounters and old reports. There is no party waiting outside: this descent belongs to one adventurer.": "Le terminal s'allume dans un bourdonnement. Un dossier de guilde vierge attend un nom. Derrière cet écran se trouve un donjon mesuré en étages, rencontres et anciens rapports. Aucun groupe ne vous attend dehors : cette descente appartient à un seul aventurier.",
    "> Register and enter": "> Enregistrer et entrer",
    "SAVE DATA IS STORED LOCALLY IN THE SOMRPG DATABASE.": "LES DONNÉES DE SAUVEGARDE SONT STOCKÉES LOCALEMENT DANS LA BASE SOMRPG.",
    "SYSTEM INFORMATION": "INFORMATIONS SYSTÈME",
    "One persistent adventurer record.": "Un dossier d'aventurier persistant.",
    "Floor-by-floor dungeon progression.": "Progression du donjon étage par étage.",
    "Automatic turn-based encounters with readable battle logs.": "Combats automatiques au tour par tour avec journaux lisibles.",
    "Experience, levels, gold, loot and equipment.": "Expérience, niveaux, or, butin et équipement.",
    "Name:": "Nom :",

    "TOWN DIRECTORY / PROTOTYPE DISTRICT": "RÉPERTOIRE DE LA VILLE / QUARTIER PROTOTYPE",
    "BROAD CLASSIC BROWSER-RPG MECHANICS // V0.4.0": "MÉCANIQUES DE RPG NAVIGATEUR CLASSIQUES // V0.5.0",
    "Town Services": "Services de la ville",
    "Everything here is intentionally modular. We can later remove, merge or rename systems that do not fit SomRPG without touching the dungeon/community core.": "Tout ici est volontairement modulaire. Nous pourrons ensuite retirer, fusionner ou renommer les systèmes qui ne correspondent pas à SomRPG sans toucher au cœur Donjon/Communauté.",
    "Adventure Board": "Tableau des aventures",
    "Training": "Entraînement",
    "Arena": "Arène",
    "Market & Stables": "Marché & Écuries",
    "Blacksmith": "Forgeron",
    "Enchanter": "Enchanteur",
    "Altar": "Autel",
    "Companions": "Compagnons",
    "Stronghold": "Forteresse",
    "Guild": "Guilde",
    "Daily Board": "Tableau quotidien",
    "Events": "Événements",
    "Adventure Points": "Points d'aventure",
    "Honor": "Honneur",
    "Aura": "Aura",
    "Mount": "Monture",
    "None": "Aucune",
    "ADVENTURE BOARD": "TABLEAU DES AVENTURES",
    "AP regenerates automatically. There is no fixed daily duration to consume.": "Les PA se régénèrent automatiquement. Il n'y a aucune durée quotidienne fixe à consommer.",
    "Complete": "Terminer",
    "No adventures configured.": "Aucune aventure configurée.",
    "TRAINING HALL": "SALLE D'ENTRAÎNEMENT",
    "Permanent base attack training.": "Entraînement permanent de l'attaque de base.",
    "Permanent base defense training.": "Entraînement permanent de la défense de base.",
    "Permanent health training (+5).": "Entraînement permanent des PV (+5).",
    "Train": "Entraîner",
    "ARENA / HALL OF HONOR": "ARÈNE / HALL D'HONNEUR",
    "Challenge": "Défier",
    "No opponents yet. Discord characters will appear here.": "Aucun adversaire pour le moment. Les personnages Discord apparaîtront ici.",
    "MARKET / STABLES": "MARCHÉ / ÉCURIES",
    "Buy": "Acheter",
    "Stables": "Écuries",
    "Hire": "Louer",
    "BLACKSMITH": "FORGERON",
    "Dismantle spare gear into Guard supplies or improve an equipment instance. Upgrade bonuses are included in combat.": "Démontez l'équipement inutilisé en ressources de garde ou améliorez une pièce. Les bonus d'amélioration sont pris en compte en combat.",
    "Upgrade": "Améliorer",
    "Dismantle": "Démonter",
    "Inventory empty.": "Inventaire vide.",
    "ENCHANTER / WITCH ANALOGUE": "ENCHANTEUR",
    "Nothing to enchant.": "Rien à enchanter.",
    "SACRIFICIAL ALTAR / AURA": "AUTEL SACRIFICIEL / AURA",
    "Offer unwanted loot for long-term Aura. Aura currently lowers Market prices.": "Sacrifiez le butin inutile pour gagner de l'Aura à long terme. L'Aura réduit actuellement les prix du marché.",
    "Sacrifice": "Sacrifier",
    "COMPANIONS / PETS": "COMPAGNONS / FAMILIERS",
    "ACTIVE": "ACTIF",
    "Activate": "Activer",
    "Recruit": "Recruter",
    "STRONGHOLD / UNDERWORLD": "FORTERESSE / SOUS-SOL",
    "Wood": "Bois",
    "Stone": "Pierre",
    "Souls": "Âmes",
    "Fortress": "Forteresse",
    "Lumber": "Scierie",
    "Quarry": "Carrière",
    "Underworld": "Sous-sol",
    "Extractor": "Extracteur",
    "GUILD HALL / RAIDS": "HALL DE GUILDE / RAIDS",
    "Treasury": "Trésorerie",
    "Instructor": "Instructeur",
    "Treasure": "Trésor",
    "Raid": "Raid",
    "Donate": "Donner",
    "Guild Raid": "Raid de guilde",
    "Found Guild — 50G": "Fonder une guilde — 50G",
    "Join": "Rejoindre",
    "DAILY BOARD / ACHIEVEMENTS / FORTUNE": "QUOTIDIEN / SUCCÈS / FORTUNE",
    "Login Reward": "Récompense de connexion",
    "Fortune Shrine": "Sanctuaire de fortune",
    "Claim Checklist": "Récupérer la liste",
    "Achievements": "Succès",
    "EVENT GATE / WORLD BOSS / TOWER": "PORTAIL D'ÉVÉNEMENT / BOSS MONDIAL / TOUR",
    "Attack World Boss": "Attaquer le boss mondial",
    "Attempt Event Floor": "Tenter l'étage événementiel",
    "No active world boss.": "Aucun boss mondial actif.",
    "No active event dungeon.": "Aucun donjon événementiel actif.",

    "Missing Courier": "Coursier disparu",
    "Track a courier lost near the old aqueduct.": "Retrouver un coursier disparu près de l'ancien aqueduc.",
    "Rat Cellar": "Cave aux rats",
    "Clear vermin from a merchant cellar.": "Éliminer les nuisibles dans la cave d'un marchand.",
    "Ruined Watchtower": "Tour de guet en ruine",
    "Search a collapsed watchtower.": "Fouiller une tour de guet effondrée.",
    "Night Patrol": "Patrouille nocturne",
    "Walk the outer wall after curfew.": "Patrouiller sur le mur extérieur après le couvre-feu.",
    "Forgotten Shrine": "Sanctuaire oublié",
    "Recover a sealed tablet from an old shrine.": "Récupérer une tablette scellée dans un ancien sanctuaire.",
    "Flame Script": "Rune de flamme",
    "Stone Ward": "Protection de pierre",
    "Twin Sigil": "Sceau double",
    "Lantern Slime": "Slime lanterne",
    "Ash Crow": "Corbeau de cendre",
    "Gate Hound": "Chien des portes",
    "Moss Lynx": "Lynx mousseux",
    "Void Mite": "Acarien du vide",
    "Forest": "Forêt",
    "Cave": "Grotte",
    "Ruins": "Ruines",
    "City": "Ville",
    "Abyss": "Abîme",
    "First Steps": "Premiers pas",
    "Reach level 2.": "Atteindre le niveau 2.",
    "Dungeon Regular": "Habitué du donjon",
    "Clear 10 dungeon floors.": "Terminer 10 étages de donjon.",
    "Working Capital": "Fonds de roulement",
    "Earn 250 gold.": "Gagner 250 pièces d'or.",
    "Apprentice Artisan": "Artisan apprenti",
    "Reach 50 Crafting XP.": "Atteindre 50 XP d'artisanat.",
    "Arena Regular": "Habitué de l'arène",
    "Win 10 arena fights.": "Gagner 10 combats d'arène.",
    "Strange Presence": "Présence étrange",
    "Reach 10 Aura.": "Atteindre 10 Aura.",
    "Archivist": "Archiviste",
    "Reach 50% Codex.": "Atteindre 50 % du Codex.",
    "Night Watch": "Veille de nuit",
    "Serve 8 total City Guard hours.": "Effectuer 8 heures totales de garde de la ville.",
    "The Bell-Tower Colossus": "Le Colosse du beffroi",
    "The Endless Stair": "L'Escalier sans fin",
    "Iron Short Sword": "Épée courte en fer",
    "A plain city-forged weapon.": "Une arme simple forgée en ville.",
    "Padded Coat": "Manteau rembourré",
    "Layered armor used by patrol recruits.": "Une armure en couches utilisée par les nouvelles recrues.",
    "Watch Captain Badge": "Insigne du capitaine de garde",
    "A badge reforged into a charm.": "Un insigne reforgé en talisman.",
    "Rune Glass": "Verre runique",
    "A shard that hums near old seals.": "Un éclat qui vibre près des anciens sceaux.",
    "Patrol Ration": "Ration de patrouille",
    "Reinforced Buckler": "Rondache renforcée"
  }));

  const patterns = [
    [/^Floor (\d+)$/i, "Étage $1"],
    [/^CAMP \/ FLOOR (\d+)$/i, "CAMP / ÉTAGE $1"],
    [/^DUNGEON ENCOUNTER \/ FLOOR (\d+)$/i, "RENCONTRE DU DONJON / ÉTAGE $1"],
    [/^> Proceed to Floor (\d+)$/i, "> Continuer vers l'étage $1"],
    [/^Recovery: ~([\d]+) seconds\.$/i, "Récupération : ~$1 secondes."],
    [/^Attack (\d+)$/i, "Attaque $1"],
    [/^Defense (\d+)$/i, "Défense $1"],
    [/^Max HP (\d+)$/i, "PV max $1"],
    [/^Tier (\d+) \(-([\d]+)% AP\)$/i, "Niveau $1 (-$2 % PA)"],
    [/^-(\d+)% AP cost for (\d+) days\.$/i, "-$1 % de coût en PA pendant $2 jours."],
    [/^(\d+) members · Raid (\d+)$/i, "$1 membres · Raid $2"],
    [/^Floor (\d+)\/(\d+)$/i, "Étage $1/$2"],
    [/^Round (\d+): (.+) deals (\d+) damage\.$/i, "Tour $1 : $2 inflige $3 dégâts."],
    [/^(.+) deals (\d+) damage\.$/i, "$1 inflige $2 dégâts."],
    [/^(.+) defeated\.$/i, "$1 vaincu."],
    [/^(.+) was defeated\.$/i, "$1 a été vaincu."],
    [/^Connected as (.+)\.$/i, "Connecté en tant que $1."],
    [/^Crafted (\d+)× (.+)\. \+(\d+) crafting XP\.$/i, "$1× $2 fabriqué. +$3 XP d'artisanat."],
    [/^Guard duty ended after (.+)\. Collected (\d+) gold and (\d+) supplies\. Partial progress was saved\.$/i, "Service terminé après $1. $2 or et $3 ressources récupérés. La progression partielle est conservée."],
    [/^HP (\d+)\/(\d+) · Your damage (\d+) · max 3 attacks\/day$/i, "PV $1/$2 · Vos dégâts $3 · max. 3 attaques/jour"],
    [/^(\d+)G reward$/i, "Récompense : $1G"]
  ];

  const originalText = new WeakMap();
  const originalAttrs = new WeakMap();

  function translateCore(core) {
    const normalized = core.replace(/\s+/g, " ").trim();
    if (!normalized) return core;
    if (fr.has(normalized)) return fr.get(normalized);
    for (const [regex, replacement] of patterns) {
      if (regex.test(normalized)) return normalized.replace(regex, replacement);
    }
    return core;
  }

  function translatedText(raw, language) {
    if (language === "en") return raw;
    const leading = raw.match(/^\s*/)?.[0] || "";
    const trailing = raw.match(/\s*$/)?.[0] || "";
    const core = raw.slice(leading.length, raw.length - trailing.length);
    return leading + translateCore(core) + trailing;
  }

  function translatableTextNodes() {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        const parent = node.parentElement;
        if (!parent) return NodeFilter.FILTER_REJECT;
        if (["SCRIPT", "STYLE", "NOSCRIPT"].includes(parent.tagName)) return NodeFilter.FILTER_REJECT;
        return node.nodeValue.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      }
    });
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    return nodes;
  }

  function applyAttributes(language) {
    document.querySelectorAll("[placeholder], [title], [aria-label]").forEach((element) => {
      if (!originalAttrs.has(element)) {
        originalAttrs.set(element, {
          placeholder: element.getAttribute("placeholder"),
          title: element.getAttribute("title"),
          ariaLabel: element.getAttribute("aria-label")
        });
      }
      const originals = originalAttrs.get(element);
      if (originals.placeholder !== null) element.setAttribute("placeholder", translatedText(originals.placeholder, language));
      if (originals.title !== null) element.setAttribute("title", translatedText(originals.title, language));
      if (originals.ariaLabel !== null) element.setAttribute("aria-label", translatedText(originals.ariaLabel, language));
    });
  }

  function applyLanguage(language) {
    const lang = language === "fr" ? "fr" : "en";
    document.documentElement.lang = lang;
    localStorage.setItem(STORAGE_KEY, lang);

    translatableTextNodes().forEach((node) => {
      if (!originalText.has(node)) originalText.set(node, node.nodeValue);
      node.nodeValue = translatedText(originalText.get(node), lang);
    });

    applyAttributes(lang);

    document.querySelectorAll("[data-language]").forEach((button) => {
      button.setAttribute("aria-pressed", button.dataset.language === lang ? "true" : "false");
    });
  }

  function initialLanguage() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === "fr" || saved === "en") return saved;
    return navigator.language && navigator.language.toLowerCase().startsWith("fr") ? "fr" : "en";
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-language]").forEach((button) => {
      button.addEventListener("click", () => applyLanguage(button.dataset.language));
    });
    applyLanguage(initialLanguage());
  });
})();
