from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from classic.models import AdventureTemplate
from classic.services import available_adventures, claim_daily_tasks, complete_adventure, daily_state, get_profile

from .views import context, get_character


def quests(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")

    profile = get_profile(character)
    profile.refresh_energy()
    _, daily, daily_tasks, daily_complete = daily_state(character)
    result = request.session.pop("quest_result", None)

    return render(
        request,
        "game/quests.html",
        context(
            request,
            character,
            quest_profile=profile,
            quests=available_adventures(character),
            daily=daily,
            daily_tasks=daily_tasks,
            daily_complete=daily_complete,
            quest_result=result,
        ),
    )


@require_POST
def complete_quest(request, quest_id):
    character = get_character(request)
    if not character:
        return redirect("create_character")

    if character.guard_active:
        request.session["quest_result"] = {"status": "guard"}
        return redirect("quests")

    quest = get_object_or_404(AdventureTemplate, pk=quest_id, enabled=True)
    ok, result = complete_adventure(character, quest)
    if not ok:
        request.session["quest_result"] = {"status": "energy", "cost": result["cost"]}
        return redirect("quests")

    request.session["quest_result"] = {
        "status": "success",
        "name": quest.name,
        "xp": result["xp"],
        "gold": result["gold"],
        "supplies": result["supplies"],
    }
    return redirect("quests")


@require_POST
def claim_quest_checklist(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")

    ok, reward = claim_daily_tasks(character)
    request.session["quest_result"] = {
        "status": "checklist" if ok else "checklist_unavailable",
        "gold": reward if ok else 0,
    }
    return redirect("quests")
