from django.conf import settings
from django.db import migrations, models
from django.utils import timezone
import django.db.models.deletion


def seed_community_content(apps, schema_editor):
    Item = apps.get_model("game", "Item")
    CraftingRecipe = apps.get_model("game", "CraftingRecipe")
    CommunitySeason = apps.get_model("game", "CommunitySeason")

    CommunitySeason.objects.get_or_create(
        slug="founders-season",
        defaults={
            "name": "Founders Season",
            "starts_at": timezone.now(),
            "active": True,
        },
    )

    ration, _ = Item.objects.get_or_create(
        name="Patrol Ration",
        defaults={
            "description": "A compact ration prepared from supplies earned during City Guard service.",
            "rarity": "common",
        },
    )
    buckler, _ = Item.objects.get_or_create(
        name="Reinforced Buckler",
        defaults={
            "description": "A small workshop shield reinforced with spare city materials.",
            "rarity": "uncommon",
            "defense_bonus": 2,
        },
    )

    CraftingRecipe.objects.get_or_create(
        name="Patrol Ration",
        defaults={
            "description": "Turn one Guard supply into a basic field ration.",
            "output_item": ration,
            "output_quantity": 1,
            "supply_cost": 1,
            "gold_cost": 0,
            "xp_reward": 3,
            "enabled": True,
        },
    )
    CraftingRecipe.objects.get_or_create(
        name="Reinforced Buckler",
        defaults={
            "description": "Use city supplies and a little gold to reinforce a defensive buckler.",
            "output_item": buckler,
            "output_quantity": 1,
            "supply_cost": 4,
            "gold_cost": 6,
            "xp_reward": 10,
            "enabled": True,
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("game", "0002_city_guard"),
    ]

    operations = [
        migrations.AddField(
            model_name="character",
            name="user",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="somrpg_character",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="character",
            name="dungeon_clears",
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="character",
            name="total_gold_earned",
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="character",
            name="crafting_xp",
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.CreateModel(
            name="CommunitySeason",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("slug", models.SlugField(max_length=100, unique=True)),
                ("starts_at", models.DateTimeField(default=timezone.now)),
                ("ends_at", models.DateTimeField(blank=True, null=True)),
                ("active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-starts_at"]},
        ),
        migrations.CreateModel(
            name="DiscordProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("discord_id", models.CharField(max_length=32, unique=True)),
                ("username", models.CharField(max_length=80)),
                ("global_name", models.CharField(blank=True, max_length=80)),
                ("avatar", models.CharField(blank=True, max_length=128)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="discord_profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="CodexDiscovery",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("entry_type", models.CharField(choices=[("enemy", "Enemy"), ("item", "Item")], max_length=16)),
                ("entry_key", models.CharField(max_length=64)),
                ("label", models.CharField(max_length=100)),
                ("discovered_at", models.DateTimeField(auto_now_add=True)),
                ("character", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="codex_discoveries", to="game.character")),
            ],
            options={"ordering": ["entry_type", "label"]},
        ),
        migrations.CreateModel(
            name="CraftingRecipe",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("description", models.CharField(blank=True, max_length=240)),
                ("output_quantity", models.PositiveIntegerField(default=1)),
                ("supply_cost", models.PositiveIntegerField(default=0)),
                ("gold_cost", models.PositiveIntegerField(default=0)),
                ("xp_reward", models.PositiveIntegerField(default=1)),
                ("enabled", models.BooleanField(default=True)),
                ("output_item", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="crafting_recipes", to="game.item")),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="SeasonProgress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("dungeon_clears", models.PositiveBigIntegerField(default=0)),
                ("commerce_gold", models.PositiveBigIntegerField(default=0)),
                ("crafting_xp", models.PositiveBigIntegerField(default=0)),
                ("joined_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("character", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="season_progress", to="game.character")),
                ("season", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="progress_entries", to="game.communityseason")),
            ],
        ),
        migrations.AddConstraint(
            model_name="codexdiscovery",
            constraint=models.UniqueConstraint(fields=("character", "entry_type", "entry_key"), name="unique_character_codex_entry"),
        ),
        migrations.AddConstraint(
            model_name="seasonprogress",
            constraint=models.UniqueConstraint(fields=("season", "character"), name="unique_season_character_progress"),
        ),
        migrations.RunPython(seed_community_content, migrations.RunPython.noop),
    ]
