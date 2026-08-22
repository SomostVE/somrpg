from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("game", "0006_sector_codex_labels")]

    operations = [
        migrations.AddField(
            model_name="character",
            name="active_title",
            field=models.CharField(blank=True, default="", max_length=40),
        ),
    ]
