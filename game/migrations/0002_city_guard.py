from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("game", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="character",
            name="guard_started_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="character",
            name="guard_gold_progress_seconds",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="character",
            name="guard_resource_progress_seconds",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="character",
            name="guard_resources",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="character",
            name="guard_total_seconds",
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="character",
            name="guard_shifts_completed",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
