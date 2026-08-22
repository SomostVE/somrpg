from django.test import TestCase

from game.models import Character
from game.navigation import navigation_for

from .models import CharacterCareer


class CareerSystemTests(TestCase):
    def test_options_is_last_menu_section(self):
        character = Character.objects.create(name="Menu Hero", floor=5)
        sections = navigation_for(character)
        self.assertEqual(sections[-1]["code"], "settings")
        self.assertEqual(sections[-1]["entries"][-1]["code"], "options")

    def test_vanguard_can_select_guardian_subclass(self):
        character = Character.objects.create(name="Guardian Hero", archetype="vanguard")
        response = self.client.post("/options/subclass/select/", {"subclass": "guardian"})
        self.assertEqual(response.status_code, 302)
        career = CharacterCareer.objects.get(character=character)
        self.assertEqual(career.subclass, "guardian")

    def test_incompatible_subclass_is_rejected(self):
        character = Character.objects.create(name="Wrong Path", archetype="vanguard")
        self.client.post("/options/subclass/select/", {"subclass": "elementalist"})
        career, _ = CharacterCareer.objects.get_or_create(character=character)
        self.assertEqual(career.subclass, "")

    def test_profession_is_independent_from_class(self):
        character = Character.objects.create(name="Smith", archetype="arcanist")
        response = self.client.post("/options/profession/select/", {"profession": "blacksmith"})
        self.assertEqual(response.status_code, 302)
        career = CharacterCareer.objects.get(character=character)
        self.assertEqual(career.profession, "blacksmith")

    def test_changing_class_clears_incompatible_subclass(self):
        character = Character.objects.create(name="Respec", archetype="vanguard", gold=100)
        CharacterCareer.objects.create(character=character, subclass="guardian", profession="merchant")
        self.client.post("/options/class/change/", {"archetype": "strider"})
        character.refresh_from_db()
        character.career_path.refresh_from_db()
        self.assertEqual(character.archetype, "strider")
        self.assertEqual(character.career_path.subclass, "")
        self.assertEqual(character.career_path.profession, "merchant")

    def test_options_lists_bilingual_careers(self):
        Character.objects.create(name="Career UI", archetype="strider")
        response = self.client.get("/options/")
        self.assertContains(response, "Duelist")
        self.assertContains(response, "Duelliste")
        self.assertContains(response, "Ranger")
        self.assertContains(response, "Rôdeur")
        self.assertContains(response, "Blacksmith")
        self.assertContains(response, "Forgeron")
