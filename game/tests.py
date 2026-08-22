from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.utils import timezone

from classic.models import AdventureTemplate

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
        self.assertContains(response, "S03")

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

    def test_navigation_uses_profile_colony_quests_and_archives_order(self):
        early = Character.objects.create(name="Early", floor=1)
        advanced = Character.objects.create(name="Advanced", floor=5)
        early_sections = navigation_for(early)
        advanced_sections = navigation_for(advanced)
        early_codes = {entry["code"] for section in early_sections for entry in section["entries"]}
        advanced_codes = {entry["code"] for section in advanced_sections for entry in section["entries"]}
        self.assertIn("profile", early_codes)
        self.assertIn("quests", early_codes)
        self.assertNotIn("character", early_codes)
        self.assertNotIn("inventory", early_codes)
        self.assertNotIn("codex", early_codes)
        self.assertNotIn("colony", early_codes)
        self.assertIn("colony", advanced_codes)
        self.assertNotIn("town", advanced_codes)
        self.assertEqual(advanced_sections[0]["code"], "player")
        self.assertEqual(advanced_sections[-1]["code"], "data")
        archive = advanced_sections[-1]["entries"][0]
        self.assertEqual(archive["label_fr"], "Archives")

    def test_visual_map_shows_full_tower_with_locked_future_sectors(self):
        Character.objects.create(name="Cartographer", floor=2)
        response = self.client.get("/tower/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "visual-floor-grid")
        self.assertContains(response, "Skybreaker Citadel")
        self.assertContains(response, "VERROUILLÉ")
        self.assertContains(response, "images/biomes/")
        self.assertContains(response, "S01")
        self.assertContains(response, "SECTEURS")

    def test_camp_has_floor_artwork_and_sector_code(self):
        Character.objects.create(name="Sightseer", floor=1)
        response = self.client.get("/")
        self.assertContains(response, "floor-art-hero")
        self.assertContains(response, "images/biomes/plains.svg")
        self.assertContains(response, "S01")
        self.assertContains(response, "SECTEUR")


class ProfileAndColonyTests(TestCase):
    def test_profile_combines_character_inventory_and_codex(self):
        character = Character.objects.create(name="Profile Hero", floor=3)
        offer = FloorShopOffer.objects.select_related("item").first()
        InventoryItem.objects.create(character=character, item=offer.item)
        response = self.client.get("/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PLAYER PROFILE")
        self.assertContains(response, "INVENTAIRE")
        self.assertContains(response, "CODEX")
        self.assertContains(response, offer.item.name)
        self.assertContains(response, "S03")

    def test_legacy_player_pages_render_unified_profile(self):
        Character.objects.create(name="Legacy Profile")
        for url in ("/character/", "/inventory/", "/codex/"):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "PLAYER PROFILE")

    def test_character_creation_prepares_colony_without_first_page_write(self):
        character = Character.objects.create(name="Prepared Founder", floor=2)
        self.assertEqual(character.colony.inhabitants, 3)

    def test_colony_page_is_available_after_floor_two(self):
        Character.objects.create(name="Founder", floor=2, gold=100)
        response = self.client.get("/colony/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "COLONIE")
        self.assertContains(response, "HABITANTS")
        self.assertContains(response, "images/biomes/settlement.svg")

    def test_local_colony_income_collection_is_atomic_and_does_not_crash(self):
        character = Character.objects.create(name="Collector", floor=2, gold=10)
        colony = character.colony
        colony.inhabitants = 10
        colony.last_gold_collected_at = timezone.now() - timedelta(hours=2, minutes=5)
        colony.save(update_fields=["inhabitants", "last_gold_collected_at"])
        response = self.client.post("/colony/collect/")
        self.assertEqual(response.status_code, 302)
        character.refresh_from_db()
        colony.refresh_from_db()
        self.assertEqual(character.gold, 14)
        self.assertGreater(colony.last_gold_collected_at, timezone.now() - timedelta(minutes=10))


class QuestTests(TestCase):
    def test_quest_board_renders_available_quests(self):
        Character.objects.create(name="Quest Hero", floor=2)
        response = self.client.get("/quests/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "QUESTS")
        self.assertContains(response, "QUÊTES")
        self.assertContains(response, "S02")
        self.assertTrue(AdventureTemplate.objects.filter(enabled=True).exists())

    def test_quest_completion_spends_energy_and_recruits_inhabitant(self):
        character = Character.objects.create(name="Quest Runner", floor=2)
        quest = AdventureTemplate.objects.filter(enabled=True).first()
        before_population = character.colony.inhabitants
        response = self.client.post(f"/quests/{quest.id}/complete/")
        self.assertEqual(response.status_code, 302)
        character.colony.refresh_from_db()
        self.assertEqual(character.colony.inhabitants, before_population + 1)
        result = self.client.session.get("quest_result")
        self.assertEqual(result["status"], "success")


class BilingualLayoutTests(TestCase):
    def test_base_layout_exposes_v0102_assets_and_dynamic_menu(self):
        Character.objects.create(name="Layout Hero")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-language="fr"')
        self.assertContains(response, 'data-language="en"')
        self.assertContains(response, "css/v090-visual.css")
        self.assertContains(response, "css/v010-colony-profile.css")
        self.assertContains(response, "css/v0102-quests.css")
        self.assertContains(response, "classic/classic.css")
        self.assertContains(response, "?v=0.12.0")
        self.assertContains(response, "VER <span id=\"version-label\">0.12.0</span>", html=False)
        self.assertContains(response, "menu-entry-profile")
        self.assertContains(response, "menu-entry-quests")
        self.assertContains(response, 'class="menu-glyph lang-fr" data-glyph="C"', html=False)
        self.assertContains(response, '<span class="lang-fr">amp</span>', html=False)
        self.assertContains(response, 'class="menu-glyph lang-fr" data-glyph="G"', html=False)
        self.assertNotContains(response, '>OR</span><span class="lang-fr">arde de la ville', html=False)
        self.assertContains(response, "quick-stats")

    def test_tower_screen_has_french_and_english_travel_labels(self):
        Character.objects.create(name="Translator", floor=3)
        response = self.client.get("/tower/")
        self.assertContains(response, "TRAVEL")
        self.assertContains(response, "ALLER")
        self.assertContains(response, "CARTE DE LA TOUR")
        self.assertContains(response, "SECTORS")
        self.assertContains(response, "SECTEURS")

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
        self.assertContains(response, "SECTEURS / LIEUX")
        self.assertContains(response, "QUÊTES")


class LiveApiTests(TestCase):
    def test_version_endpoint_is_not_cached(self):
        response = self.client.get("/api/version/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["version"], "0.12.0")
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
