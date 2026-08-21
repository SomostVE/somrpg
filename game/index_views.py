from django.db.models import Q
from django.shortcuts import redirect, render

from classic.models import (
    Achievement,
    AdventureTemplate,
    CompanionSpecies,
    Enchantment,
    EventBoss,
    EventDungeon,
)

from .models import CraftingRecipe, Enemy, Item, TowerFloor
from .views import context, get_character


def content_index(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")

    floors = TowerFloor.objects.select_related("boss_gate__enemy").all()
    cities = floors.filter(
        Q(biome__icontains="city")
        | Q(biome__icontains="settlement")
        | Q(name__icontains="market")
        | Q(name__icontains="quarter")
    )

    return render(
        request,
        "game/content_index.html",
        context(
            request,
            character,
            enemies=Enemy.objects.filter(enabled=True).select_related("loot").order_by("floor_min", "is_boss", "name"),
            items=Item.objects.all().order_by("unlock_floor", "slot", "name"),
            floors=floors,
            cities=cities,
            recipes=CraftingRecipe.objects.filter(enabled=True).select_related("output_item").order_by("name"),
            adventures=AdventureTemplate.objects.filter(enabled=True).order_by("difficulty", "energy_cost", "name"),
            companions=CompanionSpecies.objects.all().order_by("habitat", "name"),
            enchantments=Enchantment.objects.all().order_by("name"),
            achievements=Achievement.objects.all().order_by("target", "name"),
            event_bosses=EventBoss.objects.all().order_by("name"),
            event_dungeons=EventDungeon.objects.all().order_by("name"),
        ),
    )
