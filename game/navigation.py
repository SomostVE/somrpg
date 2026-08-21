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


NAVIGATION = [
    NavigationEntry("profile", "Profile", "Profil", "profile", 1, "player"),
    NavigationEntry("camp", "Camp", "Camp", "home", 1, "core"),
    NavigationEntry("tower", "Tower", "Tour", "tower_map", 1, "core"),
    NavigationEntry("explore", "Explore", "Donjon", "explore", 1, "core"),
    NavigationEntry("shop", "Floor Shop", "Boutique d'étage", "floor_shop", 1, "core"),
    NavigationEntry("guard", "City Guard", "Garde de la ville", "city_guard", 2, "systems"),
    NavigationEntry("workshop", "Workshop", "Atelier", "workshop", 3, "systems"),
    NavigationEntry("colony", "Colony", "Colonie", "colony", 2, "systems"),
    NavigationEntry("community", "Community", "Communauté", "community", 1, "network"),
    NavigationEntry("index", "Archives", "Archives", "content_index", 1, "data"),
]


SECTION_LABELS = {
    "player": ("PLAYER", "JOUEUR"),
    "core": ("ASCENT", "ASCENSION"),
    "systems": ("SERVICES", "SERVICES"),
    "network": ("NETWORK", "RÉSEAU"),
    "data": ("ARCHIVES", "ARCHIVES"),
}


def navigation_for(character):
    floor = character.floor if character else 1
    sections = []
    for section_code in ("player", "core", "systems", "network", "data"):
        entries = []
        for entry in NAVIGATION:
            if entry.section != section_code or entry.unlock_floor > floor:
                continue
            entries.append(
                {
                    "code": entry.code,
                    "label_en": entry.label_en,
                    "label_fr": entry.label_fr,
                    "label_en_rest": entry.label_en[1:],
                    "label_fr_rest": entry.label_fr[1:],
                    "marker_en": entry.label_en[:1],
                    "marker_fr": entry.label_fr[:1],
                    "href": reverse(entry.route),
                    "unlock_floor": entry.unlock_floor,
                }
            )
        if entries:
            en, fr = SECTION_LABELS[section_code]
            sections.append({"code": section_code, "label_en": en, "label_fr": fr, "entries": entries})
    return sections
