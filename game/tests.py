from datetime import date, datetime
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.utils import timezone

from .models import Character, CommunitySeason, DiscordProfile, SeasonProgress
from .services import build_standings
from .timekeeping import game_day_key, next_reset_at
from .views import get_character


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


class BilingualLayoutTests(TestCase):
    def test_base_layout_exposes_language_switcher_versioned_assets_and_compact_shell(self):
        Character.objects.create(name="Layout Hero")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-language="fr"')
        self.assertContains(response, 'data-language="en"')
        self.assertContains(response, "css/v06-shell.css")
        self.assertContains(response, "js/live-shell.js")
        self.assertContains(response, "?v=0.6.0")
        self.assertContains(response, "VER <span id=\"version-label\">0.6.0</span>", html=False)
        self.assertContains(response, "quick-stats")

    def test_authenticated_layout_contains_live_chat(self):
        user = User.objects.create_user(username="chat_user")
        Character.objects.create(user=user, name="Chat Hero")
        self.client.force_login(user)
        response = self.client.get("/")
        self.assertContains(response, 'id="live-chat-messages"')
        self.assertContains(response, 'id="live-chat-form"')


class LiveApiTests(TestCase):
    def test_version_endpoint_is_not_cached(self):
        response = self.client.get("/api/version/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["version"], "0.6.0")
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
