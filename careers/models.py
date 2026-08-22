from django.db import models

from .catalog import PROFESSION_INFO, SUBCLASS_INFO


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
