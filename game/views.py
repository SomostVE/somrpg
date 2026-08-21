from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import CharacterCreateForm
from .models import Character, Enemy, InventoryItem
from .services import resolve_encounter


def get_character(): return Character.objects.order_by("id").first()


def context(character, **extra): return {"character": character, "version": settings.SOMRPG_VERSION, **extra}


def home(request):
    character = get_character()
    if not character: return redirect("create_character")
    return render(request, "game/home.html", context(character))


def create_character(request):
    if get_character(): return redirect("home")
    form = CharacterCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request, "Your adventure begins on Floor 1."); return redirect("home")
    return render(request, "game/create_character.html", {"form": form, "version": settings.SOMRPG_VERSION})


def character_sheet(request):
    character = get_character()
    if not character: return redirect("create_character")
    return render(request, "game/character.html", context(character))


def inventory(request):
    character = get_character()
    if not character: return redirect("create_character")
    return render(request, "game/inventory.html", context(character, entries=character.inventory.select_related("item").all()))


@require_POST
def toggle_equip(request, entry_id):
    character = get_character()
    if not character: return redirect("create_character")
    entry = get_object_or_404(InventoryItem, id=entry_id, character=character)
    entry.equipped = not entry.equipped; entry.save(update_fields=["equipped"])
    return redirect("inventory")


def explore(request):
    character = get_character()
    if not character: return redirect("create_character")
    enemy = Enemy.objects.filter(enabled=True, floor_min__lte=character.floor).order_by("-floor_min", "id").first()
    if not enemy:
        messages.warning(request, "No enemy is configured for this floor yet."); return redirect("home")
    result = None
    if request.method == "POST":
        result = resolve_encounter(character, enemy)
        messages.success(request, f"{enemy.name} defeated.") if result.victory else messages.error(request, f"{character.name} was defeated.")
        character.refresh_from_db()
    return render(request, "game/explore.html", context(character, enemy=enemy, result=result))
