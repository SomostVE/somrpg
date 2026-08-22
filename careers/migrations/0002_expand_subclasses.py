from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("careers", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="charactercareer",
            name="subclass",
            field=models.CharField(
                blank=True,
                choices=[
                    ("guardian", "Guardian"),
                    ("berserker", "Berserker"),
                    ("duelist", "Duelist"),
                    ("ranger", "Ranger"),
                    ("elementalist", "Elementalist"),
                    ("spellblade", "Spellblade"),
                    ("templar", "Templar"),
                    ("crusader", "Crusader"),
                    ("assassin", "Assassin"),
                    ("shadow", "Shadow"),
                    ("pugilist", "Pugilist"),
                    ("ascetic", "Ascetic"),
                    ("priest", "Priest"),
                    ("exorcist", "Exorcist"),
                    ("beastmaster", "Beastmaster"),
                    ("marksman", "Marksman"),
                    ("reaper", "Reaper"),
                    ("gravebinder", "Gravebinder"),
                    ("skald", "Skald"),
                    ("minstrel", "Minstrel"),
                    ("dragoon", "Dragoon"),
                    ("phalanx", "Phalanx"),
                    ("sword_saint", "Sword Saint"),
                    ("ronin", "Ronin"),
                ],
                default="",
                max_length=24,
            ),
        ),
    ]
