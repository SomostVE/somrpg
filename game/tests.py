from datetime import date, datetime
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.utils import timezone

from .models import Character, CommunitySeason, DiscordProfile, FloorShopOffer, InventoryItem, SeasonProgress, TowerFloor
from .navigation import navigation_for
from .services import build_standings
from .timekeeping import game_day_key, next_reset_at
from .tower import floor_encounter
from .views import ACTIVE_FLOOR_SESSION_KEY, get_character


User = get_user_model()
PARIS = ZoneInfo("Europe/Paris")


class CommunityRankingTests(TestCase):
    def setUp(self):
        CommunitySeason.objects.all().delete()
        self.season = CommunitySeason.objects.create(
            name="Test Season",
            slug="test-season",
            starts_at=timezone.now(),
            active=True,
        )
        self.user_a = User.objects.create_user(username="discord_a")
        self.user_b = User.objects.create_user(username="discord_b")
        DiscordProfile.objects.create(user=self.user_a, discord_id="1001", username="Alpha")
        DiscordProfile.objects.create(user=self.user_b, discord_id="1002", username="Beta")
        self.char_a = Character.objects.create(user=self.user_a, name="A")
        self.char_b = Character.objects.create(user=self.user_b, name="B")

    def test_coefficients_make_commerce_more_valuable_than_dungeon(self):
        SeasonProgress.objects.create(season=self.season, character=self.char_a, dungeon_clears=10)
        SeasonProgress.objects.create(season=self.season, character=self.char_b, commerce_gold=100)
        standings = build_standings(self.season)
        self.assertEqual(standings[0]["character"], self.char_b)
        self.assertEqual(standings[0]["global_rank"], 1)
        self.assertGreater(standings[0]["global_score"], standings[1]["global_score"])

    def test_discord_display_name_is_used_in_standings(self):
        SeasonProgress.objects.create(season=self.season, character=self.char_a, dungeon_clears=1)
        standings = build_standings(self.season)
        self.assertEqual(standings[0]["display_name"], "Alpha")


class CharacterOwnershipTests(TestCase):
    def test_authenticated_players_receive_their_own_character(self):
        user_a = User.objects.create_user(username="discord_a")
        user_b = User.objects.create_user(username="discord_b")
        char_a = Character.objects.create(user=user_a, name="Alpha Hero")
        Character.objects.create(user=user_b, name="Beta Hero")
        request = RequestFactory().get("/")
        request.user = user_a
        self.assertEqual(get_character(request), char_a)

    def test_anonymous_local_mode_uses_unowned_save(self):
        local_character = Character.objects.create(name="Local Hero")
        request = RequestFactory().get("/")
        request.user = type("Anonymous", (), {"is_authenticated": False})()
        self.assertEqual(get_character(request), local_character)


class TowerProgressionTests(TestCase):
    def test_seeded_tower_has_twenty_floors_and_progressive_shop(self):
        self.assertEqual(TowerFloor.objects.count(), 20)
        self.assertTrue(FloorShopOffer.objects.filter(unlock_floor=1).exists())
        self.assertTrue(FloorShopOffer.objects.filter(unlock_floor=20).exists())

    def test_boss_gate_is_used_on_frontier_floor_five(self):
        character = Character.objects.create(name="Boss Tester", floor=5)
        enemy, is_boss = floor_encounter(character, 5)
        self.assertTrue(is_boss)
        self.assertTrue(enemy.is_boss)
        self.assertEqual(enemy.floor_min, 5)

    def test_cleared_boss_floor_uses_normal_encounter_when_revisited(self):
        character = Character.objects.create(name="Return Tester", floor=8)
        enemy, is_boss = floor_encounter(character, 5)
        self.assertFalse(is_boss)
        self.assertIsNotNone(enemy)
        self.assertFalse(enemy.is_boss)

    def test_can_travel_between_unlocked_floors_without_losing_progress(self):
        character = Character.objects.create(name="Traveler", floor=7)
        response = self.client.post("/tower/3/travel/")
        self.assertEqual(response.status_code, 302)
        character.refresh_from_db()
        self.assertEqual(character.floor, 7)
        self.assertEqual(self.client.session[ACTIVE_FLOOR_SESSION_KEY], 3)

    def test_future_floor_cannot_be_selected(self):
        Character.objects.create(name="Traveler", floor=4)
        self.client.post("/tower/8/travel/")
        self.assertEqual(self.client.session.get(ACTIVE_FLOOR_SESSION_KEY), None)

    def test_shop_uses_selected_floor_stock(self):
        Character.objects.create(name="Shop Traveler", floor=10, gold=999)
        self.client.post("/tower/3/travel/")
        response = self.client.get("/shop/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hunter Dagger")
        self.assertNotContains(response, "Skybreaker Saber")

    def test_equipping_same_slot_replaces_previous_item(self):
        character = Character.objects.create(name="Gear Tester", floor=10)
        offers = list(FloorShopOffer.objects.filter(item__slot="weapon", unlock_floor__lte=10).select_related("item")[:2])
        first = InventoryItem.objects.create(character=character, item=offers[0].item, equipped=True)
        second = InventoryItem.objects.create(character=character, item=offers[1].item)
        self.client.post(f"/inventory/{second.id}/equip/")
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertFalse(first.equipped)
        self.assertTrue(second.equipped)

    def test_archetypes_change_effective_stats(self):
        vanguard = Character.objects.create(name="V", archetype="vanguard")
        strider = Character.objects.create(name="S", archetype="strider")
        arcanist = Character.objects.create(name="A", archetype="arcanist")
        self.assertGreater(vanguard.combat_max_hp, strider.combat_max_hp)
        self.assertGreater(arcanist.total_attack, vanguard.total_attack)

    def test_navigation_unlocks_services_and_always_exposes_index(self):
        early = Character.objects.create(name="Early", floor=1)
        advanced = Character.objects.create(name="Advanced", floor=5)
        early_codes = {entry["code"] for section in navigation_for(early) for entry in section["entries"]}
        advanced_codes = {entry["code"] for section in navigation_for(advanced) for entry in section["entries"]}
        self.assertIn("index", early_codes)
        self.assertNotIn("guard", early_codes)
        self.assertNotIn("town", early_codes)
        self.assertIn("guard", advanced_codes)
        self.assertIn("town", advanced_codes)


class BilingualLayoutTests(TestCase):
    def test_base_layout_exposes_v080_assets_and_dynamic_menu(self):
        Character.objects.create(name="Layout Hero")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-language="fr"')
        self.assertContains(response, 'data-language="en"')
        self.assertContains(response, "css/v080-compact.css")
        self.assertContains(response, "js/i18n-content-v080.js")
        self.assertContains(response, "?v=0.8.0")
        self.assertContains(response, "VER <span id=\"version-label\">0.8.0</span>", html=False)
        self.assertContains(response, "menu-entry-index")
        self.assertContains(response, "quick-stats")

    def test_tower_screen_has_french_and_english_travel_labels(self):
        Character.objects.create(name="Translator", floor=3)
        response = self.client.get("/tower/")
        self.assertContains(response, "Travel")
        self.assertContains(response, "Aller")
        self.assertContains(response, "Carte des")

    def test_authenticated_layout_contains_live_chat(self):
        user = User.objects.create_user(username="chat_user")
        Character.objects.create(user=user, name="Chat Hero")
        self.client.force_login(user)
        response = self.client.get("/")
        self.assertContains(response, 'id="live-chat-messages"')
        self.assertContains(response, 'id="live-chat-form"')

    def test_local_mode_keeps_chat_column_visible_but_locked(self):
        Character.objects.create(name="Local Chat Hero")
        response = self.client.get("/")
        self.assertContains(response, 'class="chat-rail"')
        self.assertContains(response, "CHAT LOCKED")
        self.assertContains(response, "CHAT VERROUILLÉ")
        self.assertNotContains(response, 'id="live-chat-form"')


class ContentIndexTests(TestCase):
    def test_index_lists_current_world_content_and_empty_npc_category(self):
        Character.objects.create(name="Indexer", floor=5)
        response = self.client.get("/index/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dungeon Slime")
        self.assertContains(response, "Bronze Arming Sword")
        self.assertContains(response, "Dawn Gate")
        self.assertContains(response, "Missing Courier")
        self.assertContains(response, "No NPC model exists yet.")
        self.assertContains(response, "Aucun PNJ n'est encore défini")


class LiveApiTests(TestCase):
    def test_version_endpoint_is_not_cached(self):
        response = self.client.get("/api/version/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["version"], "0.8.0")
        self.assertEqual(response.json()["reset_hour"], 22)
        self.assertIn("no-store", response["Cache-Control"])

    def test_chat_requires_authenticated_account(self):
        response = self.client.get("/api/chat/?fresh=1")
        self.assertEqual(response.status_code, 403)

    def test_authenticated_chat_starts_without_history(self):
        user = User.objects.create_user(username="chat_user")
        self.client.force_login(user)
        response = self.client.get("/api/chat/?fresh=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["messages"], [])


class ParisResetTests(TestCase):
    def test_game_day_changes_at_22_paris(self):
        before = datetime(2026, 8, 21, 21, 59, tzinfo=PARIS)
        after = datetime(2026, 8, 21, 22, 0, tzinfo=PARIS)
        self.assertEqual(game_day_key(before), date(2026, 8, 20))
        self.assertEqual(game_day_key(after), date(2026, 8, 21))

    def test_next_reset_is_22_paris(self):
        current = datetime(2026, 8, 21, 16, 0, tzinfo=PARIS)
        reset = next_reset_at(current)
        self.assertEqual(reset.hour, 22)
        self.assertEqual(reset.date(), date(2026, 8, 21))
