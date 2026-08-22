from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from careers.catalog import CLASS_INFO, PROFESSION_INFO, SUBCLASS_INFO
from careers.models import CharacterCareer

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


def _career_for(character):
    if not character:
        return None
    career, _ = CharacterCareer.objects.get_or_create(character=character)
    return career


def _signed(value):
    return f"+{value}" if value > 0 else str(value)


def _classes():
    rows = []
    for code, info in CLASS_INFO.items():
        bonus_en = []
        bonus_fr = []
        if info["health"]:
            bonus_en.append(f"{_signed(info['health'])} Health")
            bonus_fr.append(f"{_signed(info['health'])} Points de vie")
        if info["attack"]:
            bonus_en.append(f"{_signed(info['attack'])} Attack")
            bonus_fr.append(f"{_signed(info['attack'])} Attaque")
        if info["defense"]:
            bonus_en.append(f"{_signed(info['defense'])} Defense")
            bonus_fr.append(f"{_signed(info['defense'])} Défense")
        rows.append(
            {
                "code": code,
                **info,
                "bonus_en": " · ".join(bonus_en) or "Balanced",
                "bonus_fr": " · ".join(bonus_fr) or "Équilibré",
            }
        )
    return rows


def _subclasses_for(character):
    if not character:
        return []
    return [
        {"code": code, **info}
        for code, info in SUBCLASS_INFO.items()
        if info["archetype"] == character.archetype
    ]


def _professions():
    return [{"code": code, **info} for code, info in PROFESSION_INFO.items()]


def options(request):
    character = get_character(request)
    characters = list(owned_characters(request))
    career = _career_for(character)
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
            career=career,
            class_options=_classes(),
            subclass_options=_subclasses_for(character),
            profession_options=_professions(),
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
    if archetype not in CLASS_INFO:
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

        career, _ = CharacterCareer.objects.select_for_update().get_or_create(character=character)
        if career.subclass and SUBCLASS_INFO.get(career.subclass, {}).get("archetype") != archetype:
            career.subclass = ""
            career.save(update_fields=["subclass", "updated_at"])

    messages.success(request, f"Class changed for {CLASS_CHANGE_COST} gold.")
    return redirect("options")


@require_POST
def select_subclass(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")

    subclass = request.POST.get("subclass", "").strip().lower()
    info = SUBCLASS_INFO.get(subclass)
    if not info or info["archetype"] != character.archetype:
        messages.error(request, "This subclass is not available for the current class.")
        return redirect("options")

    career, _ = CharacterCareer.objects.get_or_create(character=character)
    career.subclass = subclass
    career.save(update_fields=["subclass", "updated_at"])
    messages.success(request, f"Subclass selected: {info['name_en']}.")
    return redirect("options")


@require_POST
def select_profession(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")

    profession = request.POST.get("profession", "").strip().lower()
    info = PROFESSION_INFO.get(profession)
    if not info:
        messages.error(request, "Unknown profession.")
        return redirect("options")

    career, _ = CharacterCareer.objects.get_or_create(character=character)
    career.profession = profession
    career.save(update_fields=["profession", "updated_at"])
    messages.success(request, f"Profession selected: {info['name_en']}.")
    return redirect("options")
