from django.test import TestCase

from .models import Character
from .views import ACTIVE_FLOOR_SESSION_KEY


class CombatRegressionTests(TestCase):
    def _select_sector(self, number):
        session = self.client.session
        session[ACTIVE_FLOOR_SESSION_KEY] = number
        session.save()

    def test_replay_sector_four_combat_resolves_for_progressed_local_character(self):
        character = Character.objects.create(
            name="Replay Fighter",
            floor=12,
            level=4,
            max_hp=70,
            attack=8,
            defense=7,
            gold=42,
        )
        self._select_sector(4)

        preview = self.client.get("/explore/")
        self.assertEqual(preview.status_code, 200)
        self.assertContains(preview, "Mistwood Wraith")

        response = self.client.post("/explore/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["result"].victory)
        self.assertContains(response, "VICTOIRE")

        character.refresh_from_db()
        self.assertEqual(character.floor, 12)
        self.assertEqual(character.dungeon_clears, 1)
        self.assertGreater(character.gold, 42)
        self.assertEqual(self.client.session[ACTIVE_FLOOR_SESSION_KEY], 4)

    def test_frontier_combat_unlocks_next_sector(self):
        character = Character.objects.create(
            name="Frontier Fighter",
            floor=4,
            max_hp=80,
            attack=20,
            defense=12,
        )
        self._select_sector(4)

        response = self.client.post("/explore/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["result"].victory)
        self.assertEqual(response.context["result"].unlocked_floor, 5)

        character.refresh_from_db()
        self.assertEqual(character.floor, 5)
        self.assertEqual(self.client.session[ACTIVE_FLOOR_SESSION_KEY], 5)
