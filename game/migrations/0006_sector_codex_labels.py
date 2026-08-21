from django.db import migrations


def sectorize_codex_labels(apps, schema_editor):
    CodexDiscovery = apps.get_model("game", "CodexDiscovery")
    for entry in CodexDiscovery.objects.filter(entry_type="floor", label__startswith="Floor ").iterator():
        entry.label = "Sector " + entry.label[len("Floor "):]
        entry.save(update_fields=["label"])


class Migration(migrations.Migration):
    dependencies = [("game", "0005_alter_enemy_options_alter_floorshopoffer_options")]

    operations = [migrations.RunPython(sectorize_codex_labels, migrations.RunPython.noop)]
