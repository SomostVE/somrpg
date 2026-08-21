from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [("classic", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Colony",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("inhabitants", models.PositiveIntegerField(default=3)),
                ("lifetime_recruited", models.PositiveBigIntegerField(default=3)),
                ("treasury_level", models.PositiveSmallIntegerField(default=0)),
                ("market_level", models.PositiveSmallIntegerField(default=0)),
                ("hunters_level", models.PositiveSmallIntegerField(default=0)),
                ("training_level", models.PositiveSmallIntegerField(default=0)),
                ("workshop_level", models.PositiveSmallIntegerField(default=0)),
                ("last_gold_collected_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("character", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="colony", to="game.character")),
            ],
        ),
    ]
