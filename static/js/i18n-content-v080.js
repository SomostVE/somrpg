(() => {
  const translations = {
    "LV": "NV",
    "HP": "PV",
    "ATK": "ATQ",
    "G": "OR",
    "SUP": "RES",
    "CRAFT": "ART.",
    "Weapon": "Arme",
    "Head": "Tête",
    "Body": "Torse",
    "Hands": "Mains",
    "Feet": "Pieds",
    "Accessory": "Accessoire",
    "Material": "Matériau",
    "Miscellaneous": "Divers",
    "Common": "Commun",
    "Uncommon": "Peu commun",
    "Epic": "Épique",
    "Legendary": "Légendaire",
    "Vanguard": "Avant-garde",
    "Strider": "Éclaireur",
    "Arcanist": "Arcaniste",
    "Fine": "Soigné",
    "Guarded": "Protégé",
    "Balanced": "Équilibré",
    "Keen": "Aiguisé",
    "Reinforced": "Renforcé",
    "Ancient": "Antique",
    "Starforged": "Forgé aux étoiles",

    "Dawn Gate": "Porte de l'Aube",
    "Grassway": "Voie des Herbes",
    "Old Mill Quarter": "Quartier du Vieux Moulin",
    "Mistwood Verge": "Lisière de Brumebois",
    "Ironroot Bastion": "Bastion Ferracine",
    "Amber Road": "Route d'Ambre",
    "Flooded Arcade": "Arcades Inondées",
    "Moonlit Orchard": "Verger au Clair de Lune",
    "Redstone Hollow": "Creux de Pierre Rouge",
    "Cathedral of Chains": "Cathédrale des Chaînes",
    "Windscar Plateau": "Plateau Balafré par le Vent",
    "Frostmarket": "Marché des Glaces",
    "Glass Marsh": "Marais de Verre",
    "Sunken Archive": "Archives Englouties",
    "Obsidian Keep": "Forteresse d'Obsidienne",
    "Starfall Fields": "Champs de Chute d'Étoiles",
    "Ashen Causeway": "Chaussée des Cendres",
    "Silver Labyrinth": "Labyrinthe d'Argent",
    "Blackwater Crown": "Couronne des Eaux Noires",
    "Skybreaker Citadel": "Citadelle Brise-Ciel",

    "Dawn Gate Market": "Marché de la Porte de l'Aube",
    "Grassway Market": "Marché de la Voie des Herbes",
    "Old Mill Quarter Market": "Marché du Vieux Moulin",
    "Mistwood Verge Market": "Marché de Brumebois",
    "Ironroot Bastion Market": "Marché du Bastion Ferracine",
    "Amber Road Market": "Marché de la Route d'Ambre",
    "Flooded Arcade Market": "Marché des Arcades Inondées",
    "Moonlit Orchard Market": "Marché du Verger au Clair de Lune",
    "Redstone Hollow Market": "Marché du Creux de Pierre Rouge",
    "Cathedral of Chains Market": "Marché de la Cathédrale des Chaînes",
    "Windscar Plateau Market": "Marché du Plateau Balafré",
    "Frostmarket Market": "Marché des Glaces",
    "Glass Marsh Market": "Marché du Marais de Verre",
    "Sunken Archive Market": "Marché des Archives Englouties",
    "Obsidian Keep Market": "Marché de la Forteresse d'Obsidienne",
    "Starfall Fields Market": "Marché des Champs d'Étoiles",
    "Ashen Causeway Market": "Marché de la Chaussée des Cendres",
    "Silver Labyrinth Market": "Marché du Labyrinthe d'Argent",
    "Blackwater Crown Market": "Marché de la Couronne des Eaux Noires",
    "Skybreaker Citadel Market": "Marché de la Citadelle Brise-Ciel",

    "greenbelt": "ceinture verte",
    "meadow": "prairie",
    "settlement": "bourg",
    "forest": "forêt",
    "fortress": "forteresse",
    "highland": "hautes terres",
    "canals": "canaux",
    "orchard": "verger",
    "canyon": "canyon",
    "cathedral": "cathédrale",
    "plateau": "plateau",
    "snow city": "ville enneigée",
    "marsh": "marais",
    "library": "bibliothèque",
    "keep": "donjon fortifié",
    "night plains": "plaines nocturnes",
    "volcanic": "zone volcanique",
    "labyrinth": "labyrinthe",
    "storm coast": "côte orageuse",
    "sky fortress": "forteresse céleste",

    "A broad first ring of grassland, low stone walls and training roads. New adventurers begin their ascent here.": "Un vaste premier anneau de prairies, de murets de pierre et de routes d'entraînement. Les nouveaux aventuriers commencent leur ascension ici.",
    "Windy roads and abandoned farmsteads surround the path toward the inner tower.": "Des routes battues par le vent et des fermes abandonnées bordent le chemin vers l'intérieur de la tour.",
    "A half-restored trade quarter where hunters and crafters begin to gather.": "Un quartier marchand partiellement restauré où chasseurs et artisans commencent à se rassembler.",
    "Dense woodland hides ruined watchposts and creatures that attack from the fog.": "Une forêt dense dissimule des postes de garde en ruine et des créatures qui attaquent depuis la brume.",
    "The first major gate. A fortified ruin seals the staircase to the higher rings.": "Le premier grand verrou. Une ruine fortifiée condamne l'escalier vers les anneaux supérieurs.",
    "A dry highland route lined with old caravans and amber-colored stone.": "Une route sèche des hautes terres bordée d'anciennes caravanes et de pierres couleur ambre.",
    "A drowned commercial district crossed by narrow walkways and black water.": "Un quartier commerçant noyé, traversé de passerelles étroites au-dessus d'eaux noires.",
    "Silver-leaf trees cover a calm ring where rare accessories first appear in shops.": "Des arbres aux feuilles argentées couvrent un anneau paisible où les premiers accessoires rares apparaissent en boutique.",
    "A red canyon network filled with ore veins, scavengers and aggressive beasts.": "Un réseau de canyons rouges rempli de filons, de pillards et de bêtes agressives.",
    "A vast chained sanctuary dominates the tenth floor and guards the next sector.": "Un immense sanctuaire enchaîné domine le dixième étage et protège le secteur suivant.",
    "Constant crosswinds sweep exposed ruins and make every crossing dangerous.": "Des vents croisés constants balayent les ruines exposées et rendent chaque traversée dangereuse.",
    "A cold merchant city built around heated tunnels. Its shops stock stronger mid-tier equipment.": "Une ville marchande glaciale bâtie autour de tunnels chauffés. Ses boutiques proposent de meilleurs équipements intermédiaires.",
    "Crystal reeds and reflective pools turn the marsh into a maze of false paths.": "Des roseaux de cristal et des bassins réfléchissants transforment le marais en dédale de faux chemins.",
    "Collapsed libraries descend below the floor surface, filled with sealed records and traps.": "Des bibliothèques effondrées s'enfoncent sous l'étage, remplies d'archives scellées et de pièges.",
    "A black citadel marks the third great progression wall of the tower.": "Une citadelle noire marque le troisième grand verrou de progression de la tour.",
    "Open plains glow with fragments that fall from the artificial sky.": "Des plaines ouvertes brillent sous les fragments qui tombent du ciel artificiel.",
    "A long causeway crosses fields of ash, furnaces and dormant siege engines.": "Une longue chaussée traverse des champs de cendres, des fourneaux et des machines de siège endormies.",
    "Metallic corridors change direction around a central market sanctuary.": "Des couloirs métalliques changent de direction autour d'un sanctuaire marchand central.",
    "A circular coastline under permanent storm clouds surrounds the final approach.": "Une côte circulaire sous des nuages d'orage permanents entoure l'approche finale.",
    "The highest currently charted floor: a citadel suspended above the cloud layer.": "L'étage le plus élevé actuellement cartographié : une citadelle suspendue au-dessus des nuages.",

    "Slime Shard": "Éclat de slime",
    "A faintly glowing fragment left behind by a dungeon slime.": "Un fragment faiblement lumineux laissé par un slime du donjon.",
    "Patrol Ration": "Ration de patrouille",
    "A compact ration prepared from supplies earned during City Guard service.": "Une ration compacte préparée avec les ressources obtenues pendant le service de garde.",
    "Reinforced Buckler": "Rondache renforcée",
    "A small workshop shield reinforced with spare city materials.": "Un petit bouclier d'atelier renforcé avec des matériaux de récupération de la ville.",
    "Bronze Arming Sword": "Épée de guerre en bronze",
    "A reliable starter weapon sold near Dawn Gate.": "Une arme de départ fiable vendue près de la Porte de l'Aube.",
    "Traveler Coat": "Manteau de voyageur",
    "Light protection for the first rings of the tower.": "Une protection légère pour les premiers anneaux de la tour.",
    "Hunter Dagger": "Dague de chasseur",
    "A fast blade favored by scouts around the Old Mill Quarter.": "Une lame rapide appréciée des éclaireurs du Quartier du Vieux Moulin.",
    "Leather Vest": "Gilet de cuir",
    "Reinforced leather made by the floor-three workshops.": "Un cuir renforcé produit par les ateliers du troisième étage.",
    "Ironroot Blade": "Lame de Ferracine",
    "A heavy blade forged from metal recovered inside the first bastion.": "Une lourde lame forgée avec du métal récupéré dans le premier bastion.",
    "Bastion Guard": "Armure du Bastion",
    "A plated coat patterned after the Ironroot defenders.": "Une armure plaquée inspirée des défenseurs de Ferracine.",
    "Moonsteel Ring": "Anneau d'acier lunaire",
    "A pale ring that improves balance between offense and defense.": "Un anneau pâle qui équilibre l'attaque et la défense.",
    "Chainbreaker Greatsword": "Espadon Brise-Chaînes",
    "A brutal weapon unlocked after the Cathedral gate.": "Une arme brutale débloquée après la porte de la Cathédrale.",
    "Cathedral Plate": "Harnois de la Cathédrale",
    "Layered armor engraved with broken chain motifs.": "Une armure en couches gravée de motifs de chaînes brisées.",
    "Frostglass Charm": "Charme de verre-givre",
    "A cold crystal charm traded in the Frostmarket.": "Un charme de cristal glacé échangé au Marché des Glaces.",
    "Obsidian Edge": "Tranchant d'Obsidienne",
    "A black weapon issued only after reaching the Obsidian Keep.": "Une arme noire disponible uniquement après avoir atteint la Forteresse d'Obsidienne.",
    "Obsidian Mantle": "Mantelet d'Obsidienne",
    "Dense layered armor made for the upper tower.": "Une armure dense en couches conçue pour les étages supérieurs.",
    "Silver Maze Circlet": "Diadème du Labyrinthe d'Argent",
    "A light circlet recovered from the Silver Labyrinth.": "Un léger diadème récupéré dans le Labyrinthe d'Argent.",
    "Skybreaker Saber": "Sabre Brise-Ciel",
    "A high-floor weapon forged for the twentieth-floor assault.": "Une arme des hauts étages forgée pour l'assaut du vingtième étage.",
    "Crownward Coat": "Manteau de la Couronne",
    "Elite armor stocked only at the Skybreaker Citadel.": "Une armure d'élite vendue uniquement à la Citadelle Brise-Ciel.",
    "Iron Short Sword": "Épée courte en fer",
    "A plain city-forged weapon.": "Une arme simple forgée en ville.",
    "Padded Coat": "Manteau rembourré",
    "Layered armor used by patrol recruits.": "Une armure en couches utilisée par les recrues de patrouille.",
    "Watch Captain Badge": "Insigne du capitaine de garde",
    "A badge reforged into a charm.": "Un insigne reforgé en talisman.",
    "Rune Glass": "Verre runique",
    "A shard that hums near old seals.": "Un éclat qui vibre près des anciens sceaux.",

    "Dungeon Slime": "Slime du donjon",
    "Field Slime": "Slime des champs",
    "Grassway Wolf": "Loup de la Voie des Herbes",
    "Mill Quarter Cutpurse": "Coupe-bourse du Vieux Moulin",
    "Mistwood Wraith": "Spectre de Brumebois",
    "Amber Road Raider": "Pillard de la Route d'Ambre",
    "Canal Lurker": "Rôdeur des canaux",
    "Orchard Stag": "Cerf du verger",
    "Redstone Golem": "Golem de Pierre Rouge",
    "Windscar Harpy": "Harpie du Plateau Balafré",
    "Frostmarket Hound": "Molosse du Marché des Glaces",
    "Glass Marsh Mimic": "Mimique du Marais de Verre",
    "Archive Sentinel": "Sentinelle des Archives",
    "Starfall Hunter": "Chasseur de Chute d'Étoiles",
    "Ashen Knight": "Chevalier des Cendres",
    "Silver Maze Construct": "Automate du Labyrinthe d'Argent",
    "Blackwater Drake": "Drake des Eaux Noires",
    "Ironroot Warden": "Gardien Ferracine",
    "Chainbound Prelate": "Prélat Enchaîné",
    "Obsidian Regent": "Régent d'Obsidienne",
    "Skybreaker Sovereign": "Souverain Brise-Ciel",
    "Gatekeeper of Ironroot": "Gardien de Ferracine",
    "Keeper of the Tenth Gate": "Gardien de la Dixième Porte",
    "Lord of the Black Keep": "Seigneur de la Forteresse Noire",
    "Guardian of the Current Summit": "Gardien du Sommet Actuel",

    "Founders Season": "Saison des Fondateurs",
    "Turn one Guard supply into a basic field ration.": "Transforme une ressource de garde en ration de terrain.",
    "Use city supplies and a little gold to reinforce a defensive buckler.": "Utilise des ressources de la ville et un peu d'or pour renforcer une rondache.",

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
    "A hot rune for offensive force.": "Une rune ardente qui renforce l'offensive.",
    "Stone Ward": "Protection de pierre",
    "A ward that reinforces protection.": "Une protection qui renforce la défense.",
    "Twin Sigil": "Sceau double",
    "A balanced inscription.": "Une inscription équilibrée.",
    "Lantern Slime": "Slime lanterne",
    "Ash Crow": "Corbeau de cendre",
    "Gate Hound": "Chien des portes",
    "Moss Lynx": "Lynx des mousses",
    "Void Mite": "Acarien du vide",
    "First Steps": "Premiers pas",
    "Reach level 2.": "Atteindre le niveau 2.",
    "Dungeon Regular": "Habitué du donjon",
    "Clear 10 dungeon floors.": "Terminer 10 étages du donjon.",
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
    "Serve 8 total City Guard hours.": "Effectuer 8 heures au total dans la garde de la ville.",
    "The Bell-Tower Colossus": "Le Colosse du Beffroi",
    "The Endless Stair": "L'Escalier Sans Fin"
  };

  const entries = Object.entries(translations).sort((a, b) => b[0].length - a[0].length);
  const originals = new WeakMap();

  function escapeRegex(value) {
    return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function caseAwareReplacement(source, replacement) {
    if (source && source === source.toUpperCase() && /[A-Z]/i.test(source)) return replacement.toUpperCase();
    return replacement;
  }

  function translateCore(core) {
    const exact = entries.find(([key]) => key.toLowerCase() === core.toLowerCase());
    if (exact) return caseAwareReplacement(core, exact[1]);

    let translated = core;
    for (const [key, replacement] of entries) {
      const regex = new RegExp(escapeRegex(key), "gi");
      translated = translated.replace(regex, (match) => caseAwareReplacement(match, replacement));
    }

    translated = translated
      .replace(/^LV\s+(\d+)/i, "NV $1")
      .replace(/\bUNLOCK\s+F(\d+)\b/gi, "DÉBLOCAGE F$1")
      .replace(/\bQTY\s+(\d+)\b/gi, "QTÉ $1")
      .replace(/\bNEW\s+ON\s+THIS\s+FLOOR\b/gi, "NOUVEAU À CET ÉTAGE");

    return translated;
  }

  function isDynamicTranslatable(core) {
    if (!core) return false;
    if (/^LV\s+\d+/i.test(core) || /\bUNLOCK\s+F\d+\b/i.test(core) || /\bQTY\s+\d+\b/i.test(core)) return true;
    const lower = core.toLowerCase();
    return entries.some(([key]) => lower.includes(key.toLowerCase()));
  }

  function apply() {
    const french = document.documentElement.lang === "fr";
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        const parent = node.parentElement;
        if (!parent || ["SCRIPT", "STYLE", "NOSCRIPT"].includes(parent.tagName)) return NodeFilter.FILTER_REJECT;
        return node.nodeValue.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      }
    });

    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (!originals.has(node)) {
        const raw = node.nodeValue;
        if (!isDynamicTranslatable(raw.trim())) continue;
        originals.set(node, raw);
      }
      const raw = originals.get(node);
      if (!raw) continue;
      const leading = raw.match(/^\s*/)?.[0] || "";
      const trailing = raw.match(/\s*$/)?.[0] || "";
      const core = raw.slice(leading.length, raw.length - trailing.length);
      node.nodeValue = french ? leading + translateCore(core) + trailing : raw;
    }
  }

  document.addEventListener("DOMContentLoaded", apply);
  new MutationObserver(apply).observe(document.documentElement, { attributes: true, attributeFilter: ["lang"] });
  new MutationObserver(apply).observe(document.body, { subtree: true, childList: true });
})();
