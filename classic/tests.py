from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from game.models import Character, InventoryItem, Item

from .models import AdventureTemplate, CompanionSpecies
from .services import (
    claim_daily_reward,
    complete_adventure,
    get_profile,
    get_stronghold,
    recruit_companion,
    sacrifice_item,
)


class ClassicSystemsTests(TestCase):
    def setUp(self):
        self.character = Character.objects.create(name="Tester", gold=100, guard_resources=50)

    def test_profile_energy_regenerates(self):
        profile = get_profile(self.character)
        profile.adventure_energy = 50
        profile.energy_updated_at = timezone.now() - timedelta(minutes=60)
        profile.save()
        profile.refresh_energy()
        self.assertGreater(profile.adventure_energy, 50)
        self.assertLessEqual(profile.adventure_energy, 100)

    def test_adventure_spends_ap_and_rewards(self):
        adventure = AdventureTemplate.objects.create(
            name="Test Route", description="test", energy_cost=10, xp_reward=5, gold_reward=7
        )
        ok, result = complete_adventure(self.character, adventure)
        self.assertTrue(ok)
        self.assertEqual(get_profile(self.character).adventure_energy, 90)
        self.assertGreaterEqual(result["gold"], 7)

    def test_daily_reward_only_once(self):
        first, reward = claim_daily_reward(self.character)
        second, _ = claim_daily_reward(self.character)
        self.assertTrue(first)
        self.assertGreater(reward, 0)
        self.assertFalse(second)

    def test_sacrifice_generates_aura(self):
        item = Item.objects.create(name="Test Relic", rarity="rare")
        entry = InventoryItem.objects.create(character=self.character, item=item)
        ok, gain = sacrifice_item(self.character, entry)
        self.assertTrue(ok)
        self.assertEqual(gain, 4)
        self.assertEqual(get_profile(self.character).aura, 4)

    def test_companion_recruitment(self):
        species = CompanionSpecies.objects.create(name="Test Hound", habitat="city", supply_cost=5)
        self.assertTrue(recruit_companion(self.character, species))
        self.assertTrue(self.character.classic_companions.filter(species=species).exists())

    def test_stronghold_is_one_per_character(self):
        self.assertEqual(get_stronghold(self.character).pk, get_stronghold(self.character).pk)

    def test_town_overview_renders_without_body_stylesheet(self):
        response = self.client.get("/town/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "VUE D'ENSEMBLE")
        self.assertEqual(response.content.decode().count("classic/classic.css"), 1)

    def test_town_section_query_renders_only_selected_service_panel(self):
        response = self.client.get("/town/?section=stronghold")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "FORTERESSE")
        self.assertNotContains(response, "VUE D'ENSEMBLE")

    def test_invalid_town_section_falls_back_to_overview(self):
        response = self.client.get("/town/?section=unknown")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "VUE D'ENSEMBLE")
