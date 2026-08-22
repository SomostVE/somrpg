from django.test import TestCase

from game.models import Character

from .catalog import CLASS_INFO, SUBCLASS_INFO
from .models import CharacterCareer


class ExpandedClassRosterTests(TestCase):
    def test_roster_contains_twelve_classes(self):
        self.assertEqual(len(CLASS_INFO), 12)
        self.assertIn("paladin", CLASS_INFO)
        self.assertIn("rogue", CLASS_INFO)
        self.assertIn("monk", CLASS_INFO)
        self.assertIn("cleric", CLASS_INFO)
        self.assertIn("hunter", CLASS_INFO)
        self.assertIn("necromancer", CLASS_INFO)
        self.assertIn("bard", CLASS_INFO)
        self.assertIn("lancer", CLASS_INFO)
        self.assertIn("samurai", CLASS_INFO)

    def test_every_class_has_two_subclasses(self):
        for archetype in CLASS_INFO:
            subclasses = [entry for entry in SUBCLASS_INFO.values() if entry["archetype"] == archetype]
            self.assertEqual(len(subclasses), 2, archetype)

    def test_new_class_bonuses_are_applied(self):
        paladin = Character.objects.create(name="Paladin", archetype="paladin")
        necromancer = Character.objects.create(name="Necromancer", archetype="necromancer")
        self.assertEqual(paladin.combat_max_hp, paladin.max_hp + 8)
        self.assertEqual(paladin.total_defense, paladin.defense + 2)
        self.assertEqual(necromancer.total_attack, necromancer.attack + 4)
        self.assertEqual(necromancer.combat_max_hp, necromancer.max_hp - 5)

    def test_new_class_can_be_selected_for_fifty_gold(self):
        character = Character.objects.create(name="Changer", archetype="vanguard", gold=70)
        response = self.client.post("/options/class/change/", {"archetype": "samurai"})
        self.assertEqual(response.status_code, 302)
        character.refresh_from_db()
        self.assertEqual(character.archetype, "samurai")
        self.assertEqual(character.gold, 20)

    def test_changing_class_clears_incompatible_subclass(self):
        character = Character.objects.create(name="Subclass Reset", archetype="rogue", gold=100)
        CharacterCareer.objects.create(character=character, subclass="assassin")
        response = self.client.post("/options/class/change/", {"archetype": "paladin"})
        self.assertEqual(response.status_code, 302)
        career = CharacterCareer.objects.get(character=character)
        self.assertEqual(career.subclass, "")

    def test_new_subclass_can_be_selected(self):
        character = Character.objects.create(name="Shadow", archetype="rogue")
        response = self.client.post("/options/subclass/select/", {"subclass": "assassin"})
        self.assertEqual(response.status_code, 302)
        career = CharacterCareer.objects.get(character=character)
        self.assertEqual(career.subclass, "assassin")

    def test_options_lists_new_classes_in_both_languages(self):
        Character.objects.create(name="Roster", archetype="vanguard", gold=100)
        response = self.client.get("/options/")
        self.assertContains(response, "Rogue")
        self.assertContains(response, "Roublard")
        self.assertContains(response, "Necromancer")
        self.assertContains(response, "Nécromancien")
        self.assertContains(response, "Samurai")
        self.assertContains(response, "Samouraï")

    def test_profile_uses_bilingual_name_for_new_class(self):
        Character.objects.create(name="Rogue Profile", archetype="rogue")
        response = self.client.get("/profile/")
        self.assertContains(response, "Rogue")
        self.assertContains(response, "Roublard")

    def test_character_creation_lists_entire_roster_in_both_languages(self):
        response = self.client.get("/start/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="archetype"', count=len(CLASS_INFO), html=False)
        for info in CLASS_INFO.values():
            self.assertContains(response, info["name_en"])
            self.assertContains(response, info["name_fr"])
        self.assertNotContains(response, "+10 HP")
        self.assertNotContains(response, "+2 DEF")
        self.assertNotContains(response, "+3 ATK")

    def test_character_creation_accepts_new_class(self):
        response = self.client.post("/start/", {"name": "Fresh Samurai", "archetype": "samurai"})
        self.assertEqual(response.status_code, 302)
        character = Character.objects.get(name="Fresh Samurai")
        self.assertEqual(character.archetype, "samurai")
        self.assertEqual(character.class_name_fr, "Samouraï")

    def test_new_class_smoke_test_on_primary_pages(self):
        Character.objects.create(name="Smoke Necromancer", archetype="necromancer", floor=20, gold=500)
        pages = (
            "/",
            "/profile/",
            "/tower/",
            "/explore/",
            "/shop/",
            "/quests/",
            "/guard/",
            "/workshop/",
            "/colony/",
            "/options/",
            "/index/",
            "/community/",
        )
        for url in pages:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
