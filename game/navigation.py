from dataclasses import dataclass

from django.urls import reverse


@dataclass(frozen=True)
class NavigationEntry:
    code: str
    label_en: str
    label_fr: str
    route: str
    unlock_floor: int = 1
    section: str = "core"
    marker: str = "·"


# Single registry for the left menu. Adding, removing or moving a system no
# longer requires rewriting the base template.
NAVIGATION = [
    NavigationEntry("camp", "Camp", "Camp", "home", 1, "core", "C"),
    NavigationEntry("tower", "Tower", "Tour", "tower_map", 1, "core", "T"),
    NavigationEntry("explore", "Explore", "Donjon", "explore", 1, "core", "D"),
    NavigationEntry("shop", "Floor Shop", "Boutique d'étage", "floor_shop", 1, "core", "$"),
    NavigationEntry("character", "Character", "Personnage", "character", 1, "player", "P"),
    NavigationEntry("inventory", "Inventory", "Inventaire", "inventory", 1, "player", "I"),
    NavigationEntry("codex", "Codex", "Codex", "codex", 1, "player", "X"),
    NavigationEntry("guard", "City Guard", "Garde de la ville", "city_guard", 2, "systems", "G"),
    NavigationEntry("workshop", "Workshop", "Atelier", "workshop", 3, "systems", "A"),
    NavigationEntry("town", "Town Systems", "Systèmes de ville", "classic:town", 5, "systems", "+"),
    NavigationEntry("community", "Community", "Communauté", "community", 1, "network", "#"),
]


SECTION_LABELS = {
    "core": ("ASCENT", "ASCENSION"),
    "player": ("PLAYER", "JOUEUR"),
    "systems": ("SERVICES", "SERVICES"),
    "network": ("NETWORK", "RÉSEAU"),
}


def navigation_for(character):
    floor = character.floor if character else 1
    sections = []
    for section_code in ("core", "player", "systems", "network"):
        entries = []
        for entry in NAVIGATION:
            if entry.section != section_code or entry.unlock_floor > floor:
                continue
            entries.append(
                {
                    "code": entry.code,
                    "label_en": entry.label_en,
                    "label_fr": entry.label_fr,
                    "href": reverse(entry.route),
                    "unlock_floor": entry.unlock_floor,
                    "marker": entry.marker,
                }
            )
        if entries:
            en, fr = SECTION_LABELS[section_code]
            sections.append({"code": section_code, "label_en": en, "label_fr": fr, "entries": entries})
    return sections
