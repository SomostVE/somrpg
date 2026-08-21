from django.db import migrations


def backfill_colonies(apps, schema_editor):
    Character = apps.get_model("game", "Character")
    Colony = apps.get_model("classic", "Colony")
    existing = set(Colony.objects.values_list("character_id", flat=True))
    Colony.objects.bulk_create(
        [Colony(character_id=character_id) for character_id in Character.objects.exclude(id__in=existing).values_list("id", flat=True)],
        ignore_conflicts=True,
    )


class Migration(migrations.Migration):
    dependencies = [("classic", "0002_colony")]

    operations = [migrations.RunPython(backfill_colonies, migrations.RunPython.noop)]
