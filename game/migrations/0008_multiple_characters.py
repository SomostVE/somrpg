from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("game", "0007_character_active_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="character",
            name="user",
            field=models.ForeignKey(
                settings.AUTH_USER_MODEL,
                null=True,
                blank=True,
                related_name="somrpg_characters",
                on_delete=django.db.models.deletion.CASCADE,
            ),
        ),
    ]
