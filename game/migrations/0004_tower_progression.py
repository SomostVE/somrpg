from django.db import migrations, models
import django.db.models.deletion


def seed_tower(apps, schema_editor):
    Item = apps.get_model("game", "Item")
    Enemy = apps.get_model("game", "Enemy")
    TowerFloor = apps.get_model("game", "TowerFloor")
    FloorBoss = apps.get_model("game", "FloorBoss")
    FloorShopOffer = apps.get_model("game", "FloorShopOffer")

    floor_data = [
        (1, "Dawn Gate", "greenbelt", "A broad first ring of grassland, low stone walls and training roads. New adventurers begin their ascent here."),
        (2, "Grassway", "meadow", "Windy roads and abandoned farmsteads surround the path toward the inner tower."),
        (3, "Old Mill Quarter", "settlement", "A half-restored trade quarter where hunters and crafters begin to gather."),
        (4, "Mistwood Verge", "forest", "Dense woodland hides ruined watchposts and creatures that attack from the fog."),
        (5, "Ironroot Bastion", "fortress", "The first major gate. A fortified ruin seals the staircase to the higher rings."),
        (6, "Amber Road", "highland", "A dry highland route lined with old caravans and amber-colored stone."),
        (7, "Flooded Arcade", "canals", "A drowned commercial district crossed by narrow walkways and black water."),
        (8, "Moonlit Orchard", "orchard", "Silver-leaf trees cover a calm ring where rare accessories first appear in shops."),
        (9, "Redstone Hollow", "canyon", "A red canyon network filled with ore veins, scavengers and aggressive beasts."),
        (10, "Cathedral of Chains", "cathedral", "A vast chained sanctuary dominates the tenth floor and guards the next sector."),
        (11, "Windscar Plateau", "plateau", "Constant crosswinds sweep exposed ruins and make every crossing dangerous."),
        (12, "Frostmarket", "snow city", "A cold merchant city built around heated tunnels. Its shops stock stronger mid-tier equipment."),
        (13, "Glass Marsh", "marsh", "Crystal reeds and reflective pools turn the marsh into a maze of false paths."),
        (14, "Sunken Archive", "library", "Collapsed libraries descend below the floor surface, filled with sealed records and traps."),
        (15, "Obsidian Keep", "keep", "A black citadel marks the third great progression wall of the tower."),
        (16, "Starfall Fields", "night plains", "Open plains glow with fragments that fall from the artificial sky."),
        (17, "Ashen Causeway", "volcanic", "A long causeway crosses fields of ash, furnaces and dormant siege engines."),
        (18, "Silver Labyrinth", "labyrinth", "Metallic corridors change direction around a central market sanctuary."),
        (19, "Blackwater Crown", "storm coast", "A circular coastline under permanent storm clouds surrounds the final approach."),
        (20, "Skybreaker Citadel", "sky fortress", "The highest currently charted floor: a citadel suspended above the cloud layer."),
    ]
    floors = {}
    for number, name, biome, description in floor_data:
        floors[number], _ = TowerFloor.objects.get_or_create(
            floor_number=number,
            defaults={
                "name": name,
                "biome": biome,
                "description": description,
                "shop_name": f"{name} Market",
                "safe_zone": True,
            },
        )

    gear = [
        ("Bronze Arming Sword", "A reliable starter weapon sold near Dawn Gate.", "common", "weapon", 2, 0, 1, 12),
        ("Traveler Coat", "Light protection for the first rings of the tower.", "common", "body", 0, 2, 1, 12),
        ("Hunter Dagger", "A fast blade favored by scouts around the Old Mill Quarter.", "uncommon", "weapon", 3, 0, 3, 26),
        ("Leather Vest", "Reinforced leather made by the floor-three workshops.", "uncommon", "body", 0, 3, 3, 24),
        ("Ironroot Blade", "A heavy blade forged from metal recovered inside the first bastion.", "rare", "weapon", 5, 0, 5, 55),
        ("Bastion Guard", "A plated coat patterned after the Ironroot defenders.", "rare", "body", 0, 5, 5, 55),
        ("Moonsteel Ring", "A pale ring that improves balance between offense and defense.", "rare", "accessory", 2, 2, 8, 85),
        ("Chainbreaker Greatsword", "A brutal weapon unlocked after the Cathedral gate.", "epic", "weapon", 7, 1, 10, 145),
        ("Cathedral Plate", "Layered armor engraved with broken chain motifs.", "epic", "body", 1, 7, 10, 145),
        ("Frostglass Charm", "A cold crystal charm traded in the Frostmarket.", "epic", "accessory", 3, 3, 12, 180),
        ("Obsidian Edge", "A black weapon issued only after reaching the Obsidian Keep.", "epic", "weapon", 9, 2, 15, 270),
        ("Obsidian Mantle", "Dense layered armor made for the upper tower.", "epic", "body", 2, 9, 15, 270),
        ("Silver Maze Circlet", "A light circlet recovered from the Silver Labyrinth.", "legendary", "head", 4, 4, 18, 390),
        ("Skybreaker Saber", "A high-floor weapon forged for the twentieth-floor assault.", "legendary", "weapon", 12, 3, 20, 520),
        ("Crownward Coat", "Elite armor stocked only at the Skybreaker Citadel.", "legendary", "body", 3, 12, 20, 520),
    ]
    items = {}
    for name, description, rarity, slot, attack, defense, unlock, price in gear:
        item, _ = Item.objects.get_or_create(
            name=name,
            defaults={
                "description": description,
                "rarity": rarity,
                "slot": slot,
                "attack_bonus": attack,
                "defense_bonus": defense,
                "unlock_floor": unlock,
                "shop_price": price,
                "shop_enabled": True,
            },
        )
        Item.objects.filter(pk=item.pk).update(
            slot=slot,
            unlock_floor=unlock,
            shop_price=price,
            shop_enabled=True,
        )
        items[name] = item
        FloorShopOffer.objects.get_or_create(
            unlock_floor=unlock,
            item=item,
            defaults={"price": price, "enabled": True},
        )

    Item.objects.filter(name="Slime Shard").update(slot="material", shop_enabled=False)
    Enemy.objects.filter(name="Dungeon Slime").update(floor_max=2, is_boss=False)

    regular_enemies = [
        ("Field Slime", 1, 2, 12, 3, 0, 8, 2, 5),
        ("Grassway Wolf", 2, 3, 18, 4, 1, 12, 3, 7),
        ("Mill Quarter Cutpurse", 3, 4, 24, 5, 2, 16, 4, 9),
        ("Mistwood Wraith", 4, 4, 30, 6, 2, 20, 5, 11),
        ("Amber Road Raider", 6, 7, 38, 7, 3, 26, 6, 13),
        ("Canal Lurker", 7, 8, 46, 8, 4, 30, 7, 15),
        ("Orchard Stag", 8, 9, 54, 9, 4, 34, 8, 17),
        ("Redstone Golem", 9, 9, 66, 10, 6, 40, 9, 19),
        ("Windscar Harpy", 11, 12, 78, 11, 6, 46, 10, 22),
        ("Frostmarket Hound", 12, 13, 88, 12, 7, 52, 11, 24),
        ("Glass Marsh Mimic", 13, 14, 98, 13, 8, 58, 12, 26),
        ("Archive Sentinel", 14, 14, 110, 14, 9, 64, 13, 28),
        ("Starfall Hunter", 16, 17, 126, 15, 10, 72, 15, 31),
        ("Ashen Knight", 17, 18, 140, 16, 11, 80, 16, 34),
        ("Silver Maze Construct", 18, 19, 156, 17, 12, 88, 18, 37),
        ("Blackwater Drake", 19, 19, 174, 18, 13, 98, 20, 40),
    ]
    for name, floor_min, floor_max, hp, attack, defense, xp, gold_min, gold_max in regular_enemies:
        Enemy.objects.get_or_create(
            name=name,
            defaults={
                "floor_min": floor_min,
                "floor_max": floor_max,
                "max_hp": hp,
                "attack": attack,
                "defense": defense,
                "xp_reward": xp,
                "gold_min": gold_min,
                "gold_max": gold_max,
                "loot_chance": 20,
                "enabled": True,
                "is_boss": False,
            },
        )

    boss_data = [
        (5, "Ironroot Warden", "Gatekeeper of Ironroot", 90, 11, 6, 65, 18, 28, "Ironroot Blade"),
        (10, "Chainbound Prelate", "Keeper of the Tenth Gate", 180, 16, 10, 130, 35, 52, "Chainbreaker Greatsword"),
        (15, "Obsidian Regent", "Lord of the Black Keep", 310, 22, 15, 220, 60, 85, "Obsidian Edge"),
        (20, "Skybreaker Sovereign", "Guardian of the Current Summit", 500, 29, 20, 360, 100, 140, "Skybreaker Saber"),
    ]
    for floor_number, name, title, hp, attack, defense, xp, gold_min, gold_max, loot_name in boss_data:
        enemy, _ = Enemy.objects.get_or_create(
            name=name,
            defaults={
                "floor_min": floor_number,
                "floor_max": floor_number,
                "is_boss": True,
                "max_hp": hp,
                "attack": attack,
                "defense": defense,
                "xp_reward": xp,
                "gold_min": gold_min,
                "gold_max": gold_max,
                "loot": items[loot_name],
                "loot_chance": 100,
                "enabled": True,
            },
        )
        Enemy.objects.filter(pk=enemy.pk).update(is_boss=True, floor_max=floor_number, loot=items[loot_name], loot_chance=100)
        FloorBoss.objects.get_or_create(
            floor=floors[floor_number],
            defaults={"enemy": enemy, "title": title},
        )


def unseed_tower(apps, schema_editor):
    # Content is intentionally kept on reverse migrations to avoid deleting
    # player-owned items that may reference seeded records.
    pass


class Migration(migrations.Migration):
    dependencies = [("game", "0003_community_rankings")]

    operations = [
        migrations.AddField(
            model_name="item",
            name="slot",
            field=models.CharField(
                choices=[
                    ("misc", "Miscellaneous"), ("weapon", "Weapon"), ("head", "Head"),
                    ("body", "Body"), ("hands", "Hands"), ("feet", "Feet"),
                    ("accessory", "Accessory"), ("material", "Material"),
                ],
                default="misc",
                max_length=16,
            ),
        ),
        migrations.AddField(model_name="item", name="unlock_floor", field=models.PositiveIntegerField(default=1)),
        migrations.AddField(model_name="item", name="shop_price", field=models.PositiveIntegerField(default=10)),
        migrations.AddField(model_name="item", name="shop_enabled", field=models.BooleanField(default=False)),
        migrations.AddField(model_name="enemy", name="floor_max", field=models.PositiveIntegerField(blank=True, null=True)),
        migrations.AddField(model_name="enemy", name="is_boss", field=models.BooleanField(default=False)),
        migrations.AddField(
            model_name="character",
            name="archetype",
            field=models.CharField(
                choices=[("vanguard", "Vanguard"), ("strider", "Strider"), ("arcanist", "Arcanist")],
                default="vanguard",
                max_length=16,
            ),
        ),
        migrations.AddField(model_name="inventoryitem", name="affix_name", field=models.CharField(blank=True, max_length=60)),
        migrations.AddField(model_name="inventoryitem", name="affix_attack_bonus", field=models.PositiveIntegerField(default=0)),
        migrations.AddField(model_name="inventoryitem", name="affix_defense_bonus", field=models.PositiveIntegerField(default=0)),
        migrations.AlterField(
            model_name="codexdiscovery",
            name="entry_type",
            field=models.CharField(choices=[("enemy", "Enemy"), ("item", "Item"), ("floor", "Floor")], max_length=16),
        ),
        migrations.CreateModel(
            name="TowerFloor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("floor_number", models.PositiveIntegerField(unique=True)),
                ("name", models.CharField(max_length=100)),
                ("biome", models.CharField(max_length=80)),
                ("description", models.CharField(max_length=360)),
                ("shop_name", models.CharField(default="Floor Market", max_length=100)),
                ("safe_zone", models.BooleanField(default=True)),
            ],
            options={"ordering": ["floor_number"]},
        ),
        migrations.CreateModel(
            name="FloorBoss",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(blank=True, max_length=100)),
                ("enemy", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="tower_boss_gates", to="game.enemy")),
                ("floor", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="boss_gate", to="game.towerfloor")),
            ],
        ),
        migrations.CreateModel(
            name="FloorShopOffer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("unlock_floor", models.PositiveIntegerField(default=1)),
                ("price", models.PositiveIntegerField(default=10)),
                ("enabled", models.BooleanField(default=True)),
                ("item", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="tower_shop_offers", to="game.item")),
            ],
            options={"ordering": ["unlock_floor", "price"]},
        ),
        migrations.AddConstraint(
            model_name="floorshopoffer",
            constraint=models.UniqueConstraint(fields=("unlock_floor", "item"), name="unique_floor_shop_offer"),
        ),
        migrations.RunPython(seed_tower, unseed_tower),
    ]
