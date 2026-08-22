from django.test import TestCase

from .models import Character, InventoryItem, Item
from .profile_views import stat_upgrade_cost


class ProfileTrainingTests(TestCase):
    def test_profile_renders_game_layout_with_inventory_on_the_right(self):
        character = Character.objects.create(name="Trainer", gold=100)
        item = Item.objects.create(name="Training Blade", slot="weapon", attack_bonus=2)
        InventoryItem.objects.create(character=character, item=item)

        response = self.client.get("/profile/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "profile-game-layout")
        self.assertContains(response, "profile-backpack-panel")
        self.assertContains(response, "CARACTÉRISTIQUES")
        self.assertContains(response, "Points de vie")
        self.assertContains(response, "sidebar-wallet")
        self.assertNotContains(response, "Or disponible")
        self.assertContains(response, "Training Blade")
        self.assertContains(response, 'action="/profile/stat/upgrade/"', html=False)
        self.assertContains(response, "data-upgrade-preview")

    def test_attack_upgrade_spends_gold_and_increases_permanent_attack(self):
        character = Character.objects.create(name="Trainer", gold=100, attack=5)
        cost = stat_upgrade_cost(character, "attack")

        response = self.client.post("/profile/stat/upgrade/", {"stat": "attack"})

        self.assertRedirects(response, "/profile/")
        character.refresh_from_db()
        self.assertEqual(character.attack, 6)
        self.assertEqual(character.gold, 100 - cost)

    def test_health_upgrade_adds_five_health_points(self):
        character = Character.objects.create(name="Trainer", gold=100, max_hp=30)
        cost = stat_upgrade_cost(character, "health")

        self.client.post("/profile/stat/upgrade/", {"stat": "health"})

        character.refresh_from_db()
        self.assertEqual(character.max_hp, 35)
        self.assertEqual(character.gold, 100 - cost)

    def test_stat_upgrade_is_rejected_when_gold_is_insufficient(self):
        character = Character.objects.create(name="Trainer", gold=0, defense=4)

        self.client.post("/profile/stat/upgrade/", {"stat": "defense"})

        character.refresh_from_db()
        self.assertEqual(character.defense, 4)
        self.assertEqual(character.gold, 0)

    def test_profile_equipment_action_returns_to_main_profile(self):
        character = Character.objects.create(name="Trainer")
        item = Item.objects.create(name="Profile Sword", slot="weapon")
        entry = InventoryItem.objects.create(character=character, item=item)

        response = self.client.post(f"/profile/inventory/{entry.id}/equip/")

        self.assertRedirects(response, "/profile/")
        entry.refresh_from_db()
        self.assertTrue(entry.equipped)
