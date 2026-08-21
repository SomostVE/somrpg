from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from classic.colony import (
    BUILDINGS,
    collect_colony_gold,
    colony_bonuses,
    get_colony,
    pending_colony_gold,
    upgrade_colony,
    upgrade_quote,
)

from .services import add_season_progress
from .views import context, get_character


BUILDING_LABELS = {
    "treasury": ("Treasury", "Trésorerie"),
    "market": ("Trading Post", "Comptoir commercial"),
    "hunters": ("Hunters' Lodge", "Pavillon des chasseurs"),
    "training": ("Training Yard", "Terrain d'entraînement"),
    "workshop": ("Artisans' Hall", "Halle des artisans"),
}


def colony(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")
    settlement = get_colony(character)
    pending_gold, pending_hours = pending_colony_gold(settlement)
    rows = []
    for code in BUILDINGS:
        quote = upgrade_quote(settlement, code)
        rows.append(
            {
                "code": code,
                "label_en": BUILDING_LABELS[code][0],
                "label_fr": BUILDING_LABELS[code][1],
                "level": quote["level"],
                "next_level": quote["next_level"],
                "cost": quote["cost"],
                "population": quote["population"],
                "available": character.gold >= quote["cost"] and settlement.inhabitants >= quote["population"],
            }
        )
    return render(
        request,
        "game/colony.html",
        context(
            request,
            character,
            colony=settlement,
            bonuses=colony_bonuses(character),
            buildings=rows,
            pending_colony_gold=pending_gold,
            pending_colony_hours=pending_hours,
        ),
    )


@require_POST
def colony_upgrade(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")
    building = request.POST.get("building", "")
    ok, quote = upgrade_colony(character, building)
    if ok:
        messages.success(request, "Colony building upgraded.")
    elif quote:
        messages.error(request, f"Need {quote['cost']} gold and {quote['population']} inhabitants.")
    else:
        messages.error(request, "Unknown colony building.")
    return redirect("colony")


@require_POST
def colony_collect(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")
    amount = collect_colony_gold(character)
    if amount:
        add_season_progress(character, commerce=amount)
        messages.success(request, f"Colony income collected: +{amount} gold.")
    else:
        messages.warning(request, "No colony income is ready yet.")
    return redirect("colony")
