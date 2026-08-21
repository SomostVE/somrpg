from django.db import migrations, models
import django.db.models.deletion


def seed_starter_content(apps, schema_editor):
    Item = apps.get_model("game", "Item")
    Enemy = apps.get_model("game", "Enemy")
    shard = Item.objects.create(name="Slime Shard", description="A faintly glowing fragment left behind by a dungeon slime.", rarity="common", defense_bonus=1)
    Enemy.objects.create(name="Dungeon Slime", floor_min=1, max_hp=12, attack=3, defense=0, xp_reward=8, gold_min=2, gold_max=5, loot=shard, loot_chance=35, enabled=True)


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name="Character", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("name", models.CharField(default="Adventurer", max_length=40)), ("level", models.PositiveIntegerField(default=1)), ("xp", models.PositiveIntegerField(default=0)), ("gold", models.PositiveIntegerField(default=0)), ("max_hp", models.PositiveIntegerField(default=30)), ("attack", models.PositiveIntegerField(default=5)), ("defense", models.PositiveIntegerField(default=1)), ("floor", models.PositiveIntegerField(default=1)), ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True))]),
        migrations.CreateModel(name="Item", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("name", models.CharField(max_length=80, unique=True)), ("description", models.CharField(blank=True, max_length=240)), ("rarity", models.CharField(choices=[("common", "Common"), ("uncommon", "Uncommon"), ("rare", "Rare"), ("epic", "Epic"), ("legendary", "Legendary")], default="common", max_length=16)), ("attack_bonus", models.PositiveIntegerField(default=0)), ("defense_bonus", models.PositiveIntegerField(default=0))]),
        migrations.CreateModel(name="Enemy", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("name", models.CharField(max_length=80, unique=True)), ("floor_min", models.PositiveIntegerField(default=1)), ("max_hp", models.PositiveIntegerField(default=10)), ("attack", models.PositiveIntegerField(default=2)), ("defense", models.PositiveIntegerField(default=0)), ("xp_reward", models.PositiveIntegerField(default=5)), ("gold_min", models.PositiveIntegerField(default=1)), ("gold_max", models.PositiveIntegerField(default=3)), ("loot_chance", models.PositiveSmallIntegerField(default=25)), ("enabled", models.BooleanField(default=True)), ("loot", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="game.item"))], options={"ordering": ["floor_min", "name"]}),
        migrations.CreateModel(name="InventoryItem", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("quantity", models.PositiveIntegerField(default=1)), ("equipped", models.BooleanField(default=False)), ("character", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="inventory", to="game.character")), ("item", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="game.item"))]),
        migrations.AddConstraint(model_name="inventoryitem", constraint=models.UniqueConstraint(fields=("character", "item"), name="unique_character_item")),
        migrations.RunPython(seed_starter_content, migrations.RunPython.noop),
    ]
