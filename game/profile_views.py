from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from classic.colony import colony_bonuses, get_colony, sell_value

from .models import CodexDiscovery, Enemy, InventoryItem, Item, TowerFloor
from .services import add_season_progress
from .views import context, get_character


def profile(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")

    entries = character.inventory.select_related("item").order_by("item__slot", "item__rarity", "item__name")
    discoveries = CodexDiscovery.objects.filter(character=character)
    enemy_entries = discoveries.filter(entry_type="enemy")
    item_entries = discoveries.filter(entry_type="item")
    floor_entries = discoveries.filter(entry_type="floor")
    colony = get_colony(character)

    inventory_rows = [
        {"entry": entry, "sell_value": sell_value(character, entry.item)}
        for entry in entries
    ]

    return render(
        request,
        "game/profile.html",
        context(
            request,
            character,
            inventory_rows=inventory_rows,
            colony=colony,
            colony_bonuses=colony_bonuses(character),
            enemy_entries=enemy_entries,
            item_entries=item_entries,
            floor_entries=floor_entries,
            enemy_total=Enemy.objects.filter(enabled=True).count(),
            item_total=Item.objects.count(),
            floor_total=TowerFloor.objects.count(),
            discovered_entries=discoveries.count(),
            completion=character.codex_completion,
        ),
    )


@require_POST
def sell_inventory_item(request, entry_id):
    character = get_character(request)
    if not character:
        return redirect("create_character")
    entry = get_object_or_404(InventoryItem.objects.select_related("item"), pk=entry_id, character=character)
    if entry.equipped:
        messages.warning(request, "Unequip the item before selling it.")
        return redirect("profile")

    value = sell_value(character, entry.item)
    if entry.quantity > 1:
        entry.quantity -= 1
        entry.save(update_fields=["quantity"])
    else:
        entry.delete()

    character.gold += value
    character.total_gold_earned += value
    character.save(update_fields=["gold", "total_gold_earned", "updated_at"])
    add_season_progress(character, commerce=value)
    messages.success(request, f"Sold for {value} gold.")
    return redirect("profile")
