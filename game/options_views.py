from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Character
from .services import get_season_progress
from .views import (
    ACTIVE_CHARACTER_SESSION_KEY,
    ACTIVE_FLOOR_SESSION_KEY,
    CHARACTER_LIMIT,
    context,
    discord_redirect_uri,
    get_character,
    owned_characters,
)

CLASS_CHANGE_COST = 50


def options(request):
    character = get_character(request)
    characters = list(owned_characters(request))
    return render(
        request,
        "game/options.html",
        context(
            request,
            character,
            characters=characters,
            character_limit=CHARACTER_LIMIT,
            class_change_cost=CLASS_CHANGE_COST,
            discord_redirect_uri=discord_redirect_uri(request),
        ),
    )


@require_POST
def select_character(request, character_id):
    character = get_object_or_404(owned_characters(request), pk=character_id)
    request.session[ACTIVE_CHARACTER_SESSION_KEY] = character.pk
    request.session[ACTIVE_FLOOR_SESSION_KEY] = character.floor
    if request.user.is_authenticated:
        get_season_progress(character)
    messages.success(request, f"Active character: {character.name}.")
    return redirect("options")


@require_POST
def change_class(request):
    current = get_character(request)
    if not current:
        return redirect("create_character")

    archetype = request.POST.get("archetype", "").strip().lower()
    valid = {code for code, _ in Character.ARCHETYPE_CHOICES}
    if archetype not in valid:
        messages.error(request, "Unknown class.")
        return redirect("options")
    if archetype == current.archetype:
        messages.warning(request, "This class is already active.")
        return redirect("options")

    with transaction.atomic():
        character = Character.objects.select_for_update().get(pk=current.pk)
        if character.gold < CLASS_CHANGE_COST:
            messages.error(request, f"You need {CLASS_CHANGE_COST} gold to change class.")
            return redirect("options")
        character.gold -= CLASS_CHANGE_COST
        character.archetype = archetype
        character.save(update_fields=["gold", "archetype", "updated_at"])

    messages.success(request, f"Class changed for {CLASS_CHANGE_COST} gold.")
    return redirect("options")
