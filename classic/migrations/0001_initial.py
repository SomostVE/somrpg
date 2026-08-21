from django.db import migrations, models
from django.utils import timezone
import django.db.models.deletion


def seed_classic_content(apps, schema_editor):
    AdventureTemplate = apps.get_model("classic", "AdventureTemplate")
    Enchantment = apps.get_model("classic", "Enchantment")
    CompanionSpecies = apps.get_model("classic", "CompanionSpecies")
    Achievement = apps.get_model("classic", "Achievement")
    EventBoss = apps.get_model("classic", "EventBoss")
    EventDungeon = apps.get_model("classic", "EventDungeon")
    Item = apps.get_model("game", "Item")

    for values in [
        ("Missing Courier", "Track a courier lost near the old aqueduct.", 10, 12, 6, 1, 1),
        ("Rat Cellar", "Clear vermin from a merchant cellar.", 15, 18, 10, 1, 2),
        ("Ruined Watchtower", "Search a collapsed watchtower.", 20, 28, 16, 2, 3),
        ("Night Patrol", "Walk the outer wall after curfew.", 25, 36, 22, 2, 4),
        ("Forgotten Shrine", "Recover a sealed tablet from an old shrine.", 30, 48, 30, 3, 5),
    ]:
        name, description, energy, xp, gold, supply, difficulty = values
        AdventureTemplate.objects.get_or_create(name=name, defaults={"description": description, "energy_cost": energy, "xp_reward": xp, "gold_reward": gold, "supply_reward": supply, "difficulty": difficulty, "enabled": True})

    for name, description, attack, defense, cost in [
        ("Flame Script", "A hot rune for offensive force.", 2, 0, 25),
        ("Stone Ward", "A ward that reinforces protection.", 0, 2, 25),
        ("Twin Sigil", "A balanced inscription.", 1, 1, 35),
    ]:
        Enchantment.objects.get_or_create(name=name, defaults={"description": description, "attack_bonus": attack, "defense_bonus": defense, "gold_cost": cost})

    for name, habitat, attack, defense, cost in [
        ("Lantern Slime", "cave", 1, 2, 8), ("Ash Crow", "ruins", 2, 1, 12), ("Gate Hound", "city", 2, 2, 18),
        ("Moss Lynx", "forest", 3, 1, 22), ("Void Mite", "abyss", 3, 3, 30),
    ]:
        CompanionSpecies.objects.get_or_create(name=name, defaults={"habitat": habitat, "base_attack": attack, "base_defense": defense, "supply_cost": cost})

    for values in [
        ("first-steps", "First Steps", "Reach level 2.", "level", 2, 10),
        ("floor-ten", "Dungeon Regular", "Clear 10 dungeon floors.", "dungeon_clears", 10, 25),
        ("merchant", "Working Capital", "Earn 250 gold.", "gold_earned", 250, 25),
        ("artisan", "Apprentice Artisan", "Reach 50 Crafting XP.", "crafting_xp", 50, 25),
        ("duelist", "Arena Regular", "Win 10 arena fights.", "arena_wins", 10, 25),
        ("aura-10", "Strange Presence", "Reach 10 Aura.", "aura", 10, 20),
        ("collector", "Archivist", "Reach 50% Codex.", "codex", 50, 30),
        ("watchman", "Night Watch", "Serve 8 total City Guard hours.", "guard_hours", 8, 30),
    ]:
        code, name, description, stat_key, target, reward = values
        Achievement.objects.get_or_create(code=code, defaults={"name": name, "description": description, "stat_key": stat_key, "target": target, "reward_gold": reward})

    EventBoss.objects.get_or_create(name="The Bell-Tower Colossus", defaults={"max_hp": 5000, "current_hp": 5000, "starts_at": timezone.now(), "active": True})
    EventDungeon.objects.get_or_create(name="The Endless Stair", defaults={"max_floor": 30, "starts_at": timezone.now(), "active": True})

    for name, description, rarity, attack, defense in [
        ("Iron Short Sword", "A plain city-forged weapon.", "common", 2, 0),
        ("Padded Coat", "Layered armor used by patrol recruits.", "common", 0, 2),
        ("Watch Captain Badge", "A badge reforged into a charm.", "uncommon", 1, 1),
        ("Rune Glass", "A shard that hums near old seals.", "rare", 2, 2),
    ]:
        Item.objects.get_or_create(name=name, defaults={"description": description, "rarity": rarity, "attack_bonus": attack, "defense_bonus": defense})


class Migration(migrations.Migration):
    initial = True
    dependencies = [("game", "0003_community_rankings")]
    operations = [
        migrations.CreateModel(name="Achievement", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("code", models.SlugField(max_length=80, unique=True)), ("name", models.CharField(max_length=100)),
            ("description", models.CharField(max_length=240)), ("stat_key", models.CharField(max_length=60)),
            ("target", models.PositiveIntegerField(default=1)), ("reward_gold", models.PositiveIntegerField(default=10)),
        ]),
        migrations.CreateModel(name="AdventureTemplate", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("name", models.CharField(max_length=100, unique=True)), ("description", models.CharField(max_length=300)),
            ("energy_cost", models.PositiveSmallIntegerField(default=10)), ("xp_reward", models.PositiveIntegerField(default=10)),
            ("gold_reward", models.PositiveIntegerField(default=5)), ("supply_reward", models.PositiveIntegerField(default=0)),
            ("difficulty", models.PositiveSmallIntegerField(default=1)), ("enabled", models.BooleanField(default=True)),
        ]),
        migrations.CreateModel(name="CompanionSpecies", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("name", models.CharField(max_length=80, unique=True)),
            ("habitat", models.CharField(choices=[("forest", "Forest"), ("cave", "Cave"), ("ruins", "Ruins"), ("city", "City"), ("abyss", "Abyss")], default="forest", max_length=16)),
            ("base_attack", models.PositiveSmallIntegerField(default=1)), ("base_defense", models.PositiveSmallIntegerField(default=1)),
            ("supply_cost", models.PositiveIntegerField(default=10)),
        ]),
        migrations.CreateModel(name="Enchantment", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("name", models.CharField(max_length=80, unique=True)), ("description", models.CharField(blank=True, max_length=240)),
            ("attack_bonus", models.PositiveIntegerField(default=0)), ("defense_bonus", models.PositiveIntegerField(default=0)),
            ("gold_cost", models.PositiveIntegerField(default=20)),
        ]),
        migrations.CreateModel(name="EventBoss", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("name", models.CharField(max_length=100)), ("max_hp", models.PositiveBigIntegerField(default=10000)),
            ("current_hp", models.PositiveBigIntegerField(default=10000)), ("starts_at", models.DateTimeField(default=timezone.now)),
            ("ends_at", models.DateTimeField(blank=True, null=True)), ("active", models.BooleanField(default=True)),
        ]),
        migrations.CreateModel(name="EventDungeon", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("name", models.CharField(max_length=100)), ("max_floor", models.PositiveIntegerField(default=50)),
            ("starts_at", models.DateTimeField(default=timezone.now)), ("ends_at", models.DateTimeField(blank=True, null=True)),
            ("active", models.BooleanField(default=True)),
        ]),
        migrations.CreateModel(name="BrowserProfile", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("adventure_energy", models.PositiveIntegerField(default=100)), ("energy_updated_at", models.DateTimeField(default=timezone.now)),
            ("honor", models.IntegerField(default=1000)), ("arena_wins", models.PositiveIntegerField(default=0)),
            ("arena_losses", models.PositiveIntegerField(default=0)), ("arena_win_streak", models.PositiveIntegerField(default=0)),
            ("arena_last_fight_at", models.DateTimeField(blank=True, null=True)), ("aura", models.PositiveIntegerField(default=0)),
            ("mount_tier", models.PositiveSmallIntegerField(default=0)), ("mount_expires_at", models.DateTimeField(blank=True, null=True)),
            ("login_streak", models.PositiveIntegerField(default=0)), ("daily_claim_date", models.DateField(blank=True, null=True)),
            ("fortune_claim_date", models.DateField(blank=True, null=True)),
            ("character", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="classic_profile", to="game.character")),
        ]),
        migrations.CreateModel(name="Stronghold", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("wood", models.PositiveBigIntegerField(default=0)), ("stone", models.PositiveBigIntegerField(default=0)),
            ("souls", models.PositiveBigIntegerField(default=0)), ("fortress_level", models.PositiveSmallIntegerField(default=1)),
            ("lumber_level", models.PositiveSmallIntegerField(default=1)), ("quarry_level", models.PositiveSmallIntegerField(default=1)),
            ("underworld_level", models.PositiveSmallIntegerField(default=0)), ("extractor_level", models.PositiveSmallIntegerField(default=0)),
            ("last_collected_at", models.DateTimeField(default=timezone.now)),
            ("character", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="classic_stronghold", to="game.character")),
        ]),
        migrations.CreateModel(name="Guild", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("name", models.CharField(max_length=80, unique=True)), ("treasury_gold", models.PositiveBigIntegerField(default=0)),
            ("instructor_level", models.PositiveSmallIntegerField(default=0)), ("treasure_level", models.PositiveSmallIntegerField(default=0)),
            ("raid_level", models.PositiveIntegerField(default=0)), ("created_at", models.DateTimeField(auto_now_add=True)),
            ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="classic_owned_guilds", to="game.character")),
        ]),
        migrations.CreateModel(name="GearEnhancement", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("upgrade_level", models.PositiveIntegerField(default=0)),
            ("enchantment", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="classic.enchantment")),
            ("inventory_item", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="classic_enhancement", to="game.inventoryitem")),
        ]),
        migrations.CreateModel(name="DailyActivity", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("date", models.DateField(default=timezone.localdate)), ("adventures", models.PositiveSmallIntegerField(default=0)),
            ("arena_wins", models.PositiveSmallIntegerField(default=0)), ("dungeon_clears", models.PositiveSmallIntegerField(default=0)),
            ("boss_hits", models.PositiveSmallIntegerField(default=0)), ("task_reward_claimed", models.BooleanField(default=False)),
            ("character", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="classic_daily_activity", to="game.character")),
        ]),
        migrations.CreateModel(name="CharacterCompanion", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("level", models.PositiveIntegerField(default=1)), ("active", models.BooleanField(default=False)),
            ("character", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="classic_companions", to="game.character")),
            ("species", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="owners", to="classic.companionspecies")),
        ]),
        migrations.CreateModel(name="ArenaBattle", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("honor_delta", models.IntegerField(default=10)), ("created_at", models.DateTimeField(auto_now_add=True)),
            ("attacker", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="classic_arena_attacks", to="game.character")),
            ("defender", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="classic_arena_defenses", to="game.character")),
            ("winner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="classic_arena_wins_log", to="game.character")),
        ], options={"ordering": ["-created_at"]}),
        migrations.CreateModel(name="GuildMembership", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("role", models.CharField(choices=[("member", "Member"), ("officer", "Officer"), ("leader", "Leader")], default="member", max_length=16)),
            ("contributed_gold", models.PositiveBigIntegerField(default=0)), ("joined_at", models.DateTimeField(auto_now_add=True)),
            ("character", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="classic_guild_membership", to="game.character")),
            ("guild", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="memberships", to="classic.guild")),
        ]),
        migrations.CreateModel(name="EventDungeonProgress", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("floor", models.PositiveIntegerField(default=1)), ("clears", models.PositiveIntegerField(default=0)),
            ("character", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="classic_event_progress", to="game.character")),
            ("dungeon", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="progress_entries", to="classic.eventdungeon")),
        ]),
        migrations.CreateModel(name="BossContribution", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("damage", models.PositiveBigIntegerField(default=0)),
            ("boss", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="contributions", to="classic.eventboss")),
            ("character", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="classic_boss_contributions", to="game.character")),
        ]),
        migrations.CreateModel(name="AchievementUnlock", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("unlocked_at", models.DateTimeField(auto_now_add=True)),
            ("achievement", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="unlocks", to="classic.achievement")),
            ("character", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="classic_achievement_unlocks", to="game.character")),
        ]),
        migrations.AddConstraint(model_name="dailyactivity", constraint=models.UniqueConstraint(fields=("character", "date"), name="classic_unique_character_daily")),
        migrations.AddConstraint(model_name="charactercompanion", constraint=models.UniqueConstraint(fields=("character", "species"), name="classic_unique_character_companion")),
        migrations.AddConstraint(model_name="achievementunlock", constraint=models.UniqueConstraint(fields=("character", "achievement"), name="classic_unique_character_achievement")),
        migrations.AddConstraint(model_name="bosscontribution", constraint=models.UniqueConstraint(fields=("boss", "character"), name="classic_unique_boss_character")),
        migrations.AddConstraint(model_name="eventdungeonprogress", constraint=models.UniqueConstraint(fields=("dungeon", "character"), name="classic_unique_event_character")),
        migrations.RunPython(seed_classic_content, migrations.RunPython.noop),
    ]
