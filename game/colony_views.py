import logging

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


logger = logging.getLogger(__name__)

BUILDING_LABELS = {
    "treasury": ("Treasury", "Trésorerie"),
    "market": ("Trading Post", "Comptoir commercial"),
    "hunters": ("Hunters' Lodge", "Pavillon des chasseurs"),
    "training": ("Training Yard", "Terrain d'entraînement"),
}

GENERIC_COLONY_ERROR = "Erreur inattendue dans la colonie / Unexpected colony error. Aucune action n'a été appliquée."


def colony(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")

    try:
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
                bonuses=colony_bonuses(character, settlement),
                buildings=rows,
                pending_colony_gold=pending_gold,
                pending_colony_hours=pending_hours,
            ),
        )
    except Exception:
        logger.exception("Unable to render colony for character %s", character.pk)
        messages.error(request, GENERIC_COLONY_ERROR)
        return redirect("home")


@require_POST
def colony_upgrade(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")
    building = request.POST.get("building", "")
    try:
        ok, quote = upgrade_colony(character, building)
    except Exception:
        logger.exception("Colony upgrade failed for character %s building %s", character.pk, building)
        messages.error(request, GENERIC_COLONY_ERROR)
        return redirect("colony")

    if ok:
        messages.success(request, "Bâtiment amélioré / Colony building upgraded.")
    elif quote:
        messages.warning(
            request,
            f"Ressources insuffisantes / Not enough resources: {quote['cost']} gold, {quote['population']} inhabitants.",
        )
    else:
        messages.error(request, "Bâtiment inconnu / Unknown colony building.")
    return redirect("colony")


@require_POST
def colony_collect(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")

    try:
        amount = collect_colony_gold(character)
        if amount and character.user_id:
            add_season_progress(character, commerce=amount)
    except Exception:
        logger.exception("Colony income collection failed for character %s", character.pk)
        messages.error(request, GENERIC_COLONY_ERROR)
        return redirect("colony")

    if amount:
        messages.success(request, f"Revenus récupérés / Income collected: +{amount} gold.")
    else:
        messages.warning(request, "Aucun revenu prêt / No colony income is ready yet.")
    return redirect("colony")
