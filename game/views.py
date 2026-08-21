from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CharacterCreateForm
from .models import Character, Enemy, InventoryItem
from .services import resolve_encounter


def get_character():
    return Character.objects.order_by("id").first()


def context(character, **extra):
    return {"character": character, "version": settings.SOMRPG_VERSION, **extra}


def format_duration(seconds):
    seconds = max(0, int(seconds))
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes = seconds // 60
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours or days:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    return " ".join(parts)


def home(request):
    character = get_character()
    if not character:
        return redirect("create_character")
    return render(request, "game/home.html", context(character))


def create_character(request):
    if get_character():
        return redirect("home")
    form = CharacterCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your adventure begins on Floor 1.")
        return redirect("home")
    return render(request, "game/create_character.html", {"form": form, "version": settings.SOMRPG_VERSION})


def character_sheet(request):
    character = get_character()
    if not character:
        return redirect("create_character")
    return render(request, "game/character.html", context(character))


def inventory(request):
    character = get_character()
    if not character:
        return redirect("create_character")
    return render(request, "game/inventory.html", context(character, entries=character.inventory.select_related("item").all()))


@require_POST
def toggle_equip(request, entry_id):
    character = get_character()
    if not character:
        return redirect("create_character")
    entry = get_object_or_404(InventoryItem, id=entry_id, character=character)
    entry.equipped = not entry.equipped
    entry.save(update_fields=["equipped"])
    return redirect("inventory")


def city_guard(request):
    character = get_character()
    if not character:
        return redirect("create_character")

    pending_gold, pending_resources, elapsed = character.guard_pending_rewards()
    total_seconds = character.guard_total_seconds + elapsed
    return render(
        request,
        "game/guard.html",
        context(
            character,
            pending_gold=pending_gold,
            pending_resources=pending_resources,
            current_shift_duration=format_duration(elapsed),
            total_guard_duration=format_duration(total_seconds),
        ),
    )


@require_POST
def guard_start(request):
    character = get_character()
    if not character:
        return redirect("create_character")

    if character.start_guard_duty():
        messages.success(request, "City Guard duty started. Return whenever you want; there is no fixed shift length.")
    else:
        messages.warning(request, "You are already on City Guard duty.")
    return redirect("city_guard")


@require_POST
def guard_stop(request):
    character = get_character()
    if not character:
        return redirect("create_character")

    if not character.guard_active:
        messages.warning(request, "No City Guard shift is currently active.")
        return redirect("city_guard")

    gold, resources, elapsed = character.stop_guard_duty()
    messages.success(
        request,
        f"Guard duty ended after {format_duration(elapsed)}. Collected {gold} gold and {resources} supplies. Partial progress was saved.",
    )
    return redirect("city_guard")


def explore(request):
    character = get_character()
    if not character:
        return redirect("create_character")

    if character.guard_active:
        messages.warning(request, "End City Guard duty before returning to dungeon exploration.")
        return redirect("city_guard")

    enemy = Enemy.objects.filter(enabled=True, floor_min__lte=character.floor).order_by("-floor_min", "id").first()
    if not enemy:
        messages.warning(request, "No enemy is configured for this floor yet.")
        return redirect("home")

    result = None
    if request.method == "POST":
        result = resolve_encounter(character, enemy)
        if result.victory:
            messages.success(request, f"{enemy.name} defeated.")
        else:
            messages.error(request, f"{character.name} was defeated.")
        character.refresh_from_db()

    return render(request, "game/explore.html", context(character, enemy=enemy, result=result))
