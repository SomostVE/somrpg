from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("game", "0008_multiple_characters"),
    ]

    operations = [
        migrations.CreateModel(
            name="CharacterCareer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("subclass", models.CharField(blank=True, choices=[("guardian", "Guardian"), ("berserker", "Berserker"), ("duelist", "Duelist"), ("ranger", "Ranger"), ("elementalist", "Elementalist"), ("spellblade", "Spellblade")], default="", max_length=24)),
                ("profession", models.CharField(blank=True, choices=[("blacksmith", "Blacksmith"), ("alchemist", "Alchemist"), ("merchant", "Merchant"), ("cook", "Cook")], default="", max_length=24)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("character", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="career_path", to="game.character")),
            ],
        ),
    ]
