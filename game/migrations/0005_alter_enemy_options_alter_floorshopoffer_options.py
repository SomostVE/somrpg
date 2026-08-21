from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("game", "0004_tower_progression")]

    operations = [
        migrations.AlterModelOptions(
            name="enemy",
            options={"ordering": ["floor_min", "is_boss", "name"]},
        ),
        migrations.AlterModelOptions(
            name="floorshopoffer",
            options={"ordering": ["unlock_floor", "price", "item__name"]},
        ),
    ]
