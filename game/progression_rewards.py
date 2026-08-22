SKILLS = (
    {
        "code": "survivor_instinct",
        "name_en": "Survivor's Instinct",
        "name_fr": "Instinct de survie",
        "description_en": "Experience in the Tower hardens the body.",
        "description_fr": "L'expérience dans la Tour endurcit le corps.",
        "objective": "level",
        "target": 3,
        "health": 10,
        "attack": 0,
        "defense": 0,
    },
    {
        "code": "frontline_reflex",
        "name_en": "Frontline Reflex",
        "name_fr": "Réflexe de première ligne",
        "description_en": "Climbing deeper improves offensive instincts.",
        "description_fr": "Gravir la Tour améliore les réflexes offensifs.",
        "objective": "floor",
        "target": 5,
        "health": 0,
        "attack": 2,
        "defense": 0,
    },
    {
        "code": "steel_nerves",
        "name_en": "Steel Nerves",
        "name_fr": "Nerfs d'acier",
        "description_en": "Repeated dungeon victories improve defensive discipline.",
        "description_fr": "Les victoires répétées dans le donjon renforcent la discipline défensive.",
        "objective": "dungeon_clears",
        "target": 15,
        "health": 0,
        "attack": 0,
        "defense": 2,
    },
    {
        "code": "artisan_focus",
        "name_en": "Artisan Focus",
        "name_fr": "Concentration d'artisan",
        "description_en": "Crafting knowledge sharpens both offense and defense.",
        "description_fr": "Le savoir artisanal améliore autant l'attaque que la défense.",
        "objective": "crafting_xp",
        "target": 25,
        "health": 0,
        "attack": 1,
        "defense": 1,
    },
)

TITLES = (
    {
        "code": "first_climber",
        "name_en": "First Climber",
        "name_fr": "Premier grimpeur",
        "description_en": "Awarded after opening the route beyond the first sector.",
        "description_fr": "Décerné après avoir ouvert la route au-delà du premier secteur.",
        "objective": "floor",
        "target": 2,
        "health": 5,
        "attack": 0,
        "defense": 0,
    },
    {
        "code": "bastion_breaker",
        "name_en": "Bastion Breaker",
        "name_fr": "Briseur du Bastion",
        "description_en": "Proof that the first major sector guardian has fallen.",
        "description_fr": "Preuve que le premier grand gardien de secteur a été vaincu.",
        "objective": "floor",
        "target": 6,
        "health": 0,
        "attack": 2,
        "defense": 0,
    },
    {
        "code": "veteran_guard",
        "name_en": "Veteran Guard",
        "name_fr": "Garde vétéran",
        "description_en": "Granted to adventurers who repeatedly protect the colony.",
        "description_fr": "Accordé aux aventuriers qui protègent régulièrement la colonie.",
        "objective": "guard_shifts_completed",
        "target": 5,
        "health": 0,
        "attack": 0,
        "defense": 2,
    },
    {
        "code": "golden_hand",
        "name_en": "Golden Hand",
        "name_fr": "Main dorée",
        "description_en": "A title for adventurers who have generated substantial wealth.",
        "description_fr": "Un titre pour les aventuriers ayant généré une richesse importante.",
        "objective": "total_gold_earned",
        "target": 250,
        "health": 5,
        "attack": 1,
        "defense": 0,
    },
)

OBJECTIVE_LABELS = {
    "level": ("Reach level {target}", "Atteindre le niveau {target}"),
    "floor": ("Reach sector {target}", "Atteindre le secteur {target}"),
    "dungeon_clears": ("Win {target} dungeon encounters", "Remporter {target} combats du donjon"),
    "crafting_xp": ("Earn {target} crafting experience", "Gagner {target} points d'expérience d'artisanat"),
    "guard_shifts_completed": ("Complete {target} guard shifts", "Terminer {target} services de garde"),
    "total_gold_earned": ("Earn {target} gold in total", "Gagner {target} or au total"),
}


def objective_value(character, objective):
    return int(getattr(character, objective, 0) or 0)


def is_earned(character, reward):
    return objective_value(character, reward["objective"]) >= reward["target"]


def earned_skills(character):
    return [reward for reward in SKILLS if is_earned(character, reward)]


def earned_titles(character):
    return [reward for reward in TITLES if is_earned(character, reward)]


def skill_bonus(character, stat):
    return sum(reward.get(stat, 0) for reward in earned_skills(character))


def title_bonus(character, stat):
    if not character.active_title:
        return 0
    reward = next((entry for entry in TITLES if entry["code"] == character.active_title), None)
    if not reward or not is_earned(character, reward):
        return 0
    return reward.get(stat, 0)


def active_title(character):
    if not character.active_title:
        return None
    return next(
        (entry for entry in TITLES if entry["code"] == character.active_title and is_earned(character, entry)),
        None,
    )


def _bonus_text(reward, language):
    labels = {
        "health": ("Health points", "Points de vie"),
        "attack": ("Attack", "Attaque"),
        "defense": ("Defense", "Défense"),
    }
    parts = []
    for stat in ("health", "attack", "defense"):
        amount = reward.get(stat, 0)
        if amount:
            label = labels[stat][0 if language == "en" else 1]
            parts.append(f"+{amount} {label}")
    return " · ".join(parts) if parts else "—"


def reward_row(character, reward):
    current = objective_value(character, reward["objective"])
    target = reward["target"]
    label_en, label_fr = OBJECTIVE_LABELS[reward["objective"]]
    return {
        **reward,
        "current": current,
        "target": target,
        "progress": min(100, int(current * 100 / target)) if target else 100,
        "earned": current >= target,
        "objective_en": label_en.format(target=target),
        "objective_fr": label_fr.format(target=target),
        "bonus_en": _bonus_text(reward, "en"),
        "bonus_fr": _bonus_text(reward, "fr"),
    }


def reward_catalog(character):
    return {
        "skills": [reward_row(character, reward) for reward in SKILLS],
        "titles": [reward_row(character, reward) for reward in TITLES],
    }
