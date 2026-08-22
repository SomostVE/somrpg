from django.db import models


SUBCLASS_INFO = {
    "guardian": {
        "archetype": "vanguard",
        "name_en": "Guardian",
        "name_fr": "Gardien",
        "description_en": "Defensive specialist built to hold the line.",
        "description_fr": "Spécialiste défensif conçu pour tenir la ligne.",
    },
    "berserker": {
        "archetype": "vanguard",
        "name_en": "Berserker",
        "name_fr": "Berserker",
        "description_en": "Aggressive fighter focused on raw pressure.",
        "description_fr": "Combattant agressif axé sur la pression brute.",
    },
    "duelist": {
        "archetype": "strider",
        "name_en": "Duelist",
        "name_fr": "Duelliste",
        "description_en": "Mobile melee specialist for precise engagements.",
        "description_fr": "Spécialiste mobile du corps à corps et des engagements précis.",
    },
    "ranger": {
        "archetype": "strider",
        "name_en": "Ranger",
        "name_fr": "Rôdeur",
        "description_en": "Explorer focused on tracking and field control.",
        "description_fr": "Explorateur spécialisé dans la traque et le contrôle du terrain.",
    },
    "elementalist": {
        "archetype": "arcanist",
        "name_en": "Elementalist",
        "name_fr": "Élémentaliste",
        "description_en": "Arcane specialist devoted to elemental power.",
        "description_fr": "Spécialiste arcanique consacré à la puissance élémentaire.",
    },
    "spellblade": {
        "archetype": "arcanist",
        "name_en": "Spellblade",
        "name_fr": "Lame-sorcier",
        "description_en": "Hybrid fighter combining weapons and magic.",
        "description_fr": "Combattant hybride mêlant armes et magie.",
    },
}

PROFESSION_INFO = {
    "blacksmith": {
        "name_en": "Blacksmith",
        "name_fr": "Forgeron",
        "description_en": "Equipment crafting and improvement.",
        "description_fr": "Fabrication et amélioration d'équipement.",
    },
    "alchemist": {
        "name_en": "Alchemist",
        "name_fr": "Alchimiste",
        "description_en": "Potions, reagents and temporary effects.",
        "description_fr": "Potions, composants et effets temporaires.",
    },
    "merchant": {
        "name_en": "Merchant",
        "name_fr": "Marchand",
        "description_en": "Trading, prices and colony commerce.",
        "description_fr": "Commerce, prix et économie de la colonie.",
    },
    "cook": {
        "name_en": "Cook",
        "name_fr": "Cuisinier",
        "description_en": "Meals and preparation bonuses.",
        "description_fr": "Repas et bonus de préparation.",
    },
}

SUBCLASS_CHOICES = [(code, data["name_en"]) for code, data in SUBCLASS_INFO.items()]
PROFESSION_CHOICES = [(code, data["name_en"]) for code, data in PROFESSION_INFO.items()]


class CharacterCareer(models.Model):
    character = models.OneToOneField(
        "game.Character",
        related_name="career_path",
        on_delete=models.CASCADE,
    )
    subclass = models.CharField(max_length=24, choices=SUBCLASS_CHOICES, blank=True, default="")
    profession = models.CharField(max_length=24, choices=PROFESSION_CHOICES, blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    def subclass_is_valid(self):
        if not self.subclass:
            return True
        info = SUBCLASS_INFO.get(self.subclass)
        return bool(info and info["archetype"] == self.character.archetype)

    def __str__(self):
        return f"{self.character} — {self.subclass or 'no subclass'} / {self.profession or 'no profession'}"
