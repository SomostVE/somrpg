from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from classic.colony import colony_bonuses, get_colony, sell_value

from .models import Character, CodexDiscovery, Enemy, InventoryItem, Item, TowerFloor
from .progression_rewards import active_title, earned_titles, reward_catalog
from .services import add_season_progress
from .views import context, get_character


PROFILE_TABS = {"character", "abilities", "inventory", "codex"}
LEGACY_PROFILE_TABS = {
    "character": "character",
    "inventory": "inventory",
    "codex": "codex",
}

STAT_UPGRADES = {
    "health": {"field": "max_hp", "amount": 5},
    "attack": {"field": "attack", "amount": 1},
    "defense": {"field": "defense", "amount": 1},
}

EQUIPMENT_SLOT_ORDER = ("head", "body", "hands", "weapon", "feet", "accessory")


def stat_upgrade_cost(character, stat):
    if stat == "health":
        return 10 + (character.max_hp // 5) * 2
    if stat == "attack":
        return 10 + character.attack * 3
    if stat == "defense":
        return 10 + character.defense * 3
    raise ValueError("Unknown stat upgrade")


def _active_profile_tab(request):
    requested = request.GET.get("tab", "").strip().lower()
    if requested in PROFILE_TABS:
        return requested

    route_name = getattr(getattr(request, "resolver_match", None), "url_name", "")
    return LEGACY_PROFILE_TABS.get(route_name, "character")


def _profile_inventory_redirect():
    return redirect(f"{reverse('profile')}?tab=inventory")


def _equipment_slots(entries):
    equipped = {entry.item.slot: entry for entry in entries if entry.equipped}
    return [{"slot": slot, "entry": equipped.get(slot)} for slot in EQUIPMENT_SLOT_ORDER]


def profile(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")

    active_profile_tab = _active_profile_tab(request)
    entries = list(
        character.inventory.select_related("item").order_by("item__slot", "item__rarity", "item__name")
    )
    discoveries = CodexDiscovery.objects.filter(character=character)
    enemy_entries = discoveries.filter(entry_type="enemy")
    item_entries = discoveries.filter(entry_type="item")
    floor_entries = discoveries.filter(entry_type="floor")
    colony = get_colony(character)
    rewards = reward_catalog(character)

    inventory_rows = [
        {"entry": entry, "sell_value": sell_value(character, entry.item)}
        for entry in entries
    ]
    stat_upgrades = {
        stat: {
            "cost": stat_upgrade_cost(character, stat),
            "affordable": character.gold >= stat_upgrade_cost(character, stat),
        }
        for stat in STAT_UPGRADES
    }

    return render(
        request,
        "game/profile.html",
        context(
            request,
            character,
            active_profile_tab=active_profile_tab,
            inventory_rows=inventory_rows,
            equipment_slots=_equipment_slots(entries),
            stat_upgrades=stat_upgrades,
            skills=rewards["skills"],
            titles=rewards["titles"],
            active_title_reward=active_title(character),
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
def activate_title(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")

    code = request.POST.get("title", "").strip()
    allowed = {reward["code"] for reward in earned_titles(character)}
    if code and code not in allowed:
        messages.error(request, "Ce titre n'est pas encore débloqué.")
        return redirect(f"{reverse('profile')}?tab=abilities")

    character.active_title = code
    character.save(update_fields=["active_title", "updated_at"])
    return redirect(f"{reverse('profile')}?tab=abilities")


@require_POST
def upgrade_stat(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")

    stat = request.POST.get("stat", "").strip().lower()
    upgrade = STAT_UPGRADES.get(stat)
    if not upgrade:
        messages.error(request, "Action impossible.")
        return redirect("profile")

    with transaction.atomic():
        locked = Character.objects.select_for_update().get(pk=character.pk)
        cost = stat_upgrade_cost(locked, stat)
        if locked.gold < cost:
            messages.error(request, "Or insuffisant.")
            return redirect("profile")

        field = upgrade["field"]
        setattr(locked, field, getattr(locked, field) + upgrade["amount"])
        locked.gold -= cost
        locked.save(update_fields=[field, "gold", "updated_at"])

    return redirect("profile")


@require_POST
def toggle_profile_equip(request, entry_id):
    character = get_character(request)
    if not character:
        return redirect("create_character")

    entry = get_object_or_404(InventoryItem.objects.select_related("item"), id=entry_id, character=character)
    if entry.item.slot in ("misc", "material"):
        messages.warning(request, "Cet objet ne peut pas être équipé.")
        return redirect("profile")

    if entry.equipped:
        entry.equipped = False
        entry.save(update_fields=["equipped"])
    else:
        character.inventory.filter(equipped=True, item__slot=entry.item.slot).exclude(pk=entry.pk).update(equipped=False)
        entry.equipped = True
        entry.save(update_fields=["equipped"])
    return redirect("profile")


@require_POST
def sell_inventory_item(request, entry_id):
    character = get_character(request)
    if not character:
        return redirect("create_character")
    entry = get_object_or_404(InventoryItem.objects.select_related("item"), pk=entry_id, character=character)
    return_to_profile = request.POST.get("return_to") == "profile"

    if entry.equipped:
        messages.warning(request, "Retirez l'objet avant de le vendre / Unequip the item before selling it.")
        return redirect("profile") if return_to_profile else _profile_inventory_redirect()

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
    messages.success(request, f"Vendu pour {value} or / Sold for {value} gold.")
    return redirect("profile") if return_to_profile else _profile_inventory_redirect()
