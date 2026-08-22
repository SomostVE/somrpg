from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0008_multiple_characters"),
    ]

    operations = [
        migrations.AlterField(
            model_name="character",
            name="archetype",
            field=models.CharField(
                choices=[
                    ("vanguard", "Vanguard"),
                    ("strider", "Strider"),
                    ("arcanist", "Arcanist"),
                    ("paladin", "Paladin"),
                    ("rogue", "Rogue"),
                    ("monk", "Monk"),
                    ("cleric", "Cleric"),
                    ("hunter", "Hunter"),
                    ("necromancer", "Necromancer"),
                    ("bard", "Bard"),
                    ("lancer", "Lancer"),
                    ("samurai", "Samurai"),
                ],
                default="vanguard",
                max_length=16,
            ),
        ),
    ]
