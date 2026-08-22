CLASS_INFO = {
    "vanguard": {
        "name_en": "Vanguard", "name_fr": "Avant-garde",
        "description_en": "Durable front-line fighter.", "description_fr": "Combattant robuste de première ligne.",
        "health": 10, "attack": 0, "defense": 2,
    },
    "strider": {
        "name_en": "Strider", "name_fr": "Éclaireur",
        "description_en": "Fast and precise mobile fighter.", "description_fr": "Combattant mobile, rapide et précis.",
        "health": 0, "attack": 2, "defense": 0,
    },
    "arcanist": {
        "name_en": "Arcanist", "name_fr": "Arcaniste",
        "description_en": "Fragile specialist with high offensive power.", "description_fr": "Spécialiste fragile doté d'une forte puissance offensive.",
        "health": -5, "attack": 3, "defense": 0,
    },
    "paladin": {
        "name_en": "Paladin", "name_fr": "Paladin",
        "description_en": "Armored protector balancing offense and defense.", "description_fr": "Protecteur en armure équilibrant attaque et défense.",
        "health": 8, "attack": 1, "defense": 2,
    },
    "rogue": {
        "name_en": "Rogue", "name_fr": "Roublard",
        "description_en": "High-risk fighter built around lethal attacks.", "description_fr": "Combattant risqué spécialisé dans les attaques létales.",
        "health": -2, "attack": 3, "defense": 0,
    },
    "monk": {
        "name_en": "Monk", "name_fr": "Moine",
        "description_en": "Balanced close-combat specialist with strong endurance.", "description_fr": "Spécialiste équilibré du corps à corps doté d'une grande endurance.",
        "health": 4, "attack": 2, "defense": 1,
    },
    "cleric": {
        "name_en": "Cleric", "name_fr": "Clerc",
        "description_en": "Resilient support fighter protected by sacred arts.", "description_fr": "Combattant de soutien résistant protégé par les arts sacrés.",
        "health": 6, "attack": 0, "defense": 2,
    },
    "hunter": {
        "name_en": "Hunter", "name_fr": "Chasseur",
        "description_en": "Versatile tracker effective in prolonged encounters.", "description_fr": "Traqueur polyvalent efficace lors des combats prolongés.",
        "health": 2, "attack": 2, "defense": 1,
    },
    "necromancer": {
        "name_en": "Necromancer", "name_fr": "Nécromancien",
        "description_en": "Dark caster trading durability for raw damage.", "description_fr": "Lanceur de sorts obscurs sacrifiant sa résistance pour les dégâts.",
        "health": -5, "attack": 4, "defense": 0,
    },
    "bard": {
        "name_en": "Bard", "name_fr": "Barde",
        "description_en": "Adaptable adventurer with no major weakness.", "description_fr": "Aventurier adaptable sans faiblesse majeure.",
        "health": 2, "attack": 1, "defense": 1,
    },
    "lancer": {
        "name_en": "Lancer", "name_fr": "Lancier",
        "description_en": "Reach fighter combining pressure and toughness.", "description_fr": "Combattant d'allonge combinant pression offensive et robustesse.",
        "health": 5, "attack": 2, "defense": 1,
    },
    "samurai": {
        "name_en": "Samurai", "name_fr": "Samouraï",
        "description_en": "Disciplined swordsman focused on decisive attacks.", "description_fr": "Épéiste discipliné spécialisé dans les attaques décisives.",
        "health": 0, "attack": 3, "defense": 1,
    },
}

CLASS_CHOICES = [(code, data["name_en"]) for code, data in CLASS_INFO.items()]

SUBCLASS_INFO = {
    "guardian": {"archetype": "vanguard", "name_en": "Guardian", "name_fr": "Gardien", "description_en": "Defensive specialist built to hold the line.", "description_fr": "Spécialiste défensif conçu pour tenir la ligne."},
    "berserker": {"archetype": "vanguard", "name_en": "Berserker", "name_fr": "Berserker", "description_en": "Aggressive fighter focused on raw pressure.", "description_fr": "Combattant agressif axé sur la pression brute."},
    "duelist": {"archetype": "strider", "name_en": "Duelist", "name_fr": "Duelliste", "description_en": "Mobile melee specialist for precise engagements.", "description_fr": "Spécialiste mobile du corps à corps et des engagements précis."},
    "ranger": {"archetype": "strider", "name_en": "Ranger", "name_fr": "Rôdeur", "description_en": "Explorer focused on tracking and field control.", "description_fr": "Explorateur spécialisé dans la traque et le contrôle du terrain."},
    "elementalist": {"archetype": "arcanist", "name_en": "Elementalist", "name_fr": "Élémentaliste", "description_en": "Arcane specialist devoted to elemental power.", "description_fr": "Spécialiste arcanique consacré à la puissance élémentaire."},
    "spellblade": {"archetype": "arcanist", "name_en": "Spellblade", "name_fr": "Lame-sorcier", "description_en": "Hybrid fighter combining weapons and magic.", "description_fr": "Combattant hybride mêlant armes et magie."},
    "templar": {"archetype": "paladin", "name_en": "Templar", "name_fr": "Templier", "description_en": "Shield-focused holy defender.", "description_fr": "Défenseur sacré spécialisé dans le bouclier."},
    "crusader": {"archetype": "paladin", "name_en": "Crusader", "name_fr": "Croisé", "description_en": "Offensive paladin who pushes the front line.", "description_fr": "Paladin offensif qui fait avancer la ligne de front."},
    "assassin": {"archetype": "rogue", "name_en": "Assassin", "name_fr": "Assassin", "description_en": "Burst specialist seeking quick eliminations.", "description_fr": "Spécialiste des dégâts explosifs et des éliminations rapides."},
    "shadow": {"archetype": "rogue", "name_en": "Shadow", "name_fr": "Ombre", "description_en": "Elusive fighter built around avoidance and openings.", "description_fr": "Combattant insaisissable exploitant l'esquive et les ouvertures."},
    "pugilist": {"archetype": "monk", "name_en": "Pugilist", "name_fr": "Pugiliste", "description_en": "Relentless hand-to-hand combatant.", "description_fr": "Combattant acharné spécialisé dans le corps à corps."},
    "ascetic": {"archetype": "monk", "name_en": "Ascetic", "name_fr": "Ascète", "description_en": "Disciplined monk focused on resilience.", "description_fr": "Moine discipliné spécialisé dans la résistance."},
    "priest": {"archetype": "cleric", "name_en": "Priest", "name_fr": "Prêtre", "description_en": "Sacred support specialist.", "description_fr": "Spécialiste du soutien sacré."},
    "exorcist": {"archetype": "cleric", "name_en": "Exorcist", "name_fr": "Exorciste", "description_en": "Battle cleric trained against corrupted enemies.", "description_fr": "Clerc de combat entraîné contre les ennemis corrompus."},
    "beastmaster": {"archetype": "hunter", "name_en": "Beastmaster", "name_fr": "Maître des bêtes", "description_en": "Hunter specialized in creatures and companions.", "description_fr": "Chasseur spécialisé dans les créatures et les compagnons."},
    "marksman": {"archetype": "hunter", "name_en": "Marksman", "name_fr": "Tireur d'élite", "description_en": "Precision hunter focused on critical openings.", "description_fr": "Chasseur de précision axé sur les ouvertures critiques."},
    "reaper": {"archetype": "necromancer", "name_en": "Reaper", "name_fr": "Faucheur", "description_en": "Necromancer who converts death into offensive power.", "description_fr": "Nécromancien transformant la mort en puissance offensive."},
    "gravebinder": {"archetype": "necromancer", "name_en": "Gravebinder", "name_fr": "Lie-tombe", "description_en": "Controller who binds spirits and weakens enemies.", "description_fr": "Contrôleur liant les esprits et affaiblissant ses ennemis."},
    "skald": {"archetype": "bard", "name_en": "Skald", "name_fr": "Skalde", "description_en": "War bard who turns songs into battle momentum.", "description_fr": "Barde de guerre transformant ses chants en élan de combat."},
    "minstrel": {"archetype": "bard", "name_en": "Minstrel", "name_fr": "Ménestrel", "description_en": "Support bard focused on preparation and utility.", "description_fr": "Barde de soutien axé sur la préparation et l'utilité."},
    "dragoon": {"archetype": "lancer", "name_en": "Dragoon", "name_fr": "Dragon", "description_en": "Aggressive lancer specialized in overwhelming charges.", "description_fr": "Lancier offensif spécialisé dans les charges dévastatrices."},
    "phalanx": {"archetype": "lancer", "name_en": "Phalanx", "name_fr": "Phalange", "description_en": "Defensive lancer who controls enemy approach.", "description_fr": "Lancier défensif contrôlant l'approche ennemie."},
    "sword_saint": {"archetype": "samurai", "name_en": "Sword Saint", "name_fr": "Saint de l'épée", "description_en": "Master swordsman devoted to perfect technique.", "description_fr": "Maître épéiste consacré à la perfection technique."},
    "ronin": {"archetype": "samurai", "name_en": "Ronin", "name_fr": "Rōnin", "description_en": "Independent warrior favoring adaptable offense.", "description_fr": "Guerrier indépendant privilégiant une offensive adaptable."},
}

PROFESSION_INFO = {
    "blacksmith": {"name_en": "Blacksmith", "name_fr": "Forgeron", "description_en": "Equipment crafting and improvement.", "description_fr": "Fabrication et amélioration d'équipement."},
    "alchemist": {"name_en": "Alchemist", "name_fr": "Alchimiste", "description_en": "Potions, reagents and temporary effects.", "description_fr": "Potions, composants et effets temporaires."},
    "merchant": {"name_en": "Merchant", "name_fr": "Marchand", "description_en": "Trading, prices and colony commerce.", "description_fr": "Commerce, prix et économie de la colonie."},
    "cook": {"name_en": "Cook", "name_fr": "Cuisinier", "description_en": "Meals and preparation bonuses.", "description_fr": "Repas et bonus de préparation."},
}
