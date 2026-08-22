from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from .models import Character, CodexDiscovery, CommunitySeason, DiscordProfile, Enemy, SeasonProgress
from .services import build_standings, resolve_encounter


User = get_user_model()


class RuntimeQueryTests(TestCase):
    def test_long_combat_does_not_query_equipment_every_round(self):
        character = Character.objects.create(
            name="Query Fighter",
            max_hp=100,
            attack=1,
            defense=100,
            floor=1,
        )
        enemy = Enemy.objects.create(
            name="Query Training Dummy",
            floor_min=1,
            floor_max=1,
            max_hp=10000,
            attack=1,
            defense=1000,
            xp_reward=1,
            gold_min=0,
            gold_max=0,
            loot_chance=0,
        )

        with CaptureQueriesContext(connection) as queries:
            result = resolve_encounter(character, enemy, 1)

        self.assertFalse(result.victory)
        self.assertEqual(len(result.rounds), 100)
        self.assertLessEqual(len(queries), 10)

    def test_community_ranking_queries_do_not_scale_per_player_codex(self):
        season = CommunitySeason.objects.create(
            name="Performance Season",
            slug="performance-season",
            starts_at=timezone.now(),
            active=True,
        )
        for index in range(12):
            user = User.objects.create_user(username=f"perf-user-{index}")
            DiscordProfile.objects.create(
                user=user,
                discord_id=f"9000{index}",
                username=f"Player {index}",
            )
            character = Character.objects.create(
                user=user,
                name=f"Performance Hero {index}",
            )
            SeasonProgress.objects.create(
                season=season,
                character=character,
                dungeon_clears=index,
                commerce_gold=index * 2,
                crafting_xp=index * 3,
            )
            CodexDiscovery.objects.create(
                character=character,
                entry_type="enemy",
                entry_key=f"perf-{index}",
                label=f"Discovery {index}",
            )

        with CaptureQueriesContext(connection) as queries:
            standings = build_standings(season)

        self.assertEqual(len(standings), 12)
        self.assertLessEqual(len(queries), 6)
