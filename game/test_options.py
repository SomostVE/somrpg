from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from .models import Character
from .views import ACTIVE_CHARACTER_SESSION_KEY


User = get_user_model()


class OptionsAndCharactersTests(TestCase):
    def test_sidebar_shows_gold_level_and_xp_and_chat_title_is_short(self):
        Character.objects.create(name="Summary Hero", level=4, xp=17, gold=23, floor=4)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Niveau")
        self.assertContains(response, "17 / 80")
        self.assertContains(response, ">CHAT<", html=False)
        self.assertNotContains(response, "CHAT EN DIRECT")

    def test_options_is_available_from_player_menu(self):
        Character.objects.create(name="Options Hero")
        response = self.client.get("/")
        self.assertContains(response, "menu-entry-options")
        response = self.client.get("/options/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "LANGUE")
        self.assertContains(response, "PERSONNAGES")
        self.assertContains(response, "CHANGEMENT DE CLASSE")

    def test_local_mode_can_switch_between_three_characters(self):
        first = Character.objects.create(name="First", floor=2)
        second = Character.objects.create(name="Second", floor=5)
        third = Character.objects.create(name="Third", floor=7)

        response = self.client.post(f"/options/character/{second.id}/select/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session[ACTIVE_CHARACTER_SESSION_KEY], second.id)
        response = self.client.get("/")
        self.assertEqual(response.context["character"], second)
        self.assertEqual(Character.objects.filter(user__isnull=True).count(), 3)
        self.assertNotEqual(first.id, third.id)

    def test_fourth_character_is_blocked(self):
        for index in range(3):
            Character.objects.create(name=f"Hero {index}")
        response = self.client.get("/start/")
        self.assertRedirects(response, "/options/")

    def test_class_change_costs_fifty_gold(self):
        character = Character.objects.create(name="Class Hero", archetype="vanguard", gold=80)
        response = self.client.post("/options/class/change/", {"archetype": "strider"})
        self.assertRedirects(response, "/options/")
        character.refresh_from_db()
        self.assertEqual(character.archetype, "strider")
        self.assertEqual(character.gold, 30)

    def test_class_change_is_rejected_without_fifty_gold(self):
        character = Character.objects.create(name="Poor Hero", archetype="vanguard", gold=49)
        self.client.post("/options/class/change/", {"archetype": "arcanist"})
        character.refresh_from_db()
        self.assertEqual(character.archetype, "vanguard")
        self.assertEqual(character.gold, 49)

    def test_authenticated_account_can_own_three_characters(self):
        user = User.objects.create_user(username="multi")
        Character.objects.create(user=user, name="One")
        Character.objects.create(user=user, name="Two")
        Character.objects.create(user=user, name="Three")
        self.assertEqual(Character.objects.filter(user=user).count(), 3)

    @override_settings(
        DISCORD_CLIENT_ID="123456",
        DISCORD_CLIENT_SECRET="secret",
        DISCORD_REDIRECT_URI="https://somrpg.example/auth/discord/callback/",
    )
    def test_discord_login_starts_interactive_oauth_flow(self):
        response = self.client.get("/auth/discord/")
        self.assertEqual(response.status_code, 302)
        parsed = urlparse(response["Location"])
        query = parse_qs(parsed.query)
        self.assertEqual(parsed.netloc, "discord.com")
        self.assertEqual(query["client_id"], ["123456"])
        self.assertEqual(query["scope"], ["identify"])
        self.assertEqual(query["redirect_uri"], ["https://somrpg.example/auth/discord/callback/"])
        self.assertNotIn("prompt", query)
        self.assertTrue(self.client.session.get("discord_oauth_state"))
