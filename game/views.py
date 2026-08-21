import secrets
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login as auth_login, logout as auth_logout
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import CharacterCreateForm
from .models import (
    Character,
    CodexDiscovery,
    CraftingRecipe,
    DiscordProfile,
    FloorShopOffer,
    InventoryItem,
    Item,
    TowerFloor,
)
from .navigation import navigation_for
from .services import (
    add_season_progress,
    build_standings,
    discover_enemy,
    discover_floor,
    discover_item,
    get_active_season,
    get_season_progress,
    resolve_encounter,
)
from .tower import (
    add_item,
    available_shop_offers,
    current_floor,
    floor_encounter,
    newly_unlocked_offers,
    visible_tower_floors,
)


User = get_user_model()
DISCORD_AUTHORIZE_URL = "https://discord.com/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
DISCORD_USER_URL = "https://discord.com/api/users/@me"


def discord_configured():
    return bool(settings.DISCORD_CLIENT_ID and settings.DISCORD_CLIENT_SECRET)


def get_character(request):
    if request.user.is_authenticated:
        return Character.objects.filter(user=request.user).first()
    return Character.objects.filter(user__isnull=True).order_by("id").first()


def context(request, character, **extra):
    floor = current_floor(character) if character else None
    return {
        "character": character,
        "version": settings.SOMRPG_VERSION,
        "discord_configured": discord_configured(),
        "discord_profile": getattr(request.user, "discord_profile", None) if request.user.is_authenticated else None,
        "navigation_sections": navigation_for(character) if character else [],
        "tower_floor": floor,
        **extra,
    }


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
    character = get_character(request)
    if not character:
        return redirect("create_character")
    floor = current_floor(character)
    discover_floor(character, floor)
    return render(
        request,
        "game/home.html",
        context(
            request,
            character,
            new_shop_offers=newly_unlocked_offers(character),
            floor_boss=getattr(floor, "boss_gate", None) if floor else None,
        ),
    )


def create_character(request):
    if get_character(request):
        return redirect("home")

    form = CharacterCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        character = form.save(commit=False)
        if request.user.is_authenticated:
            character.user = request.user
        character.save()
        discover_floor(character, current_floor(character))
        if request.user.is_authenticated:
            get_season_progress(character)
        messages.success(request, "Your ascent begins on Floor 1.")
        return redirect("home")

    return render(request, "game/create_character.html", context(request, None, form=form))


def character_sheet(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")
    return render(request, "game/character.html", context(request, character))


def tower_map(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")
    floors = visible_tower_floors(character, future=2)
    return render(request, "game/tower.html", context(request, character, floors=floors))


def floor_shop(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")
    offers = available_shop_offers(character)
    return render(
        request,
        "game/shop.html",
        context(
            request,
            character,
            offers=offers,
            new_offers=offers.filter(unlock_floor=character.floor),
        ),
    )


@require_POST
def buy_floor_shop_item(request, offer_id):
    character = get_character(request)
    if not character:
        return redirect("create_character")
    offer = get_object_or_404(
        FloorShopOffer.objects.select_related("item"),
        id=offer_id,
        enabled=True,
        unlock_floor__lte=character.floor,
    )
    if character.gold < offer.price:
        messages.error(request, "Not enough gold for this item.")
        return redirect("floor_shop")

    character.gold -= offer.price
    character.save(update_fields=["gold", "updated_at"])
    entry, _ = add_item(character, offer.item, floor_number=character.floor)
    discover_item(character, offer.item)
    messages.success(request, f"Purchased {entry.display_name} for {offer.price} gold.")
    return redirect("floor_shop")


def inventory(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")
    entries = character.inventory.select_related("item").order_by("item__slot", "item__rarity", "item__name")
    return render(request, "game/inventory.html", context(request, character, entries=entries))


@require_POST
def toggle_equip(request, entry_id):
    character = get_character(request)
    if not character:
        return redirect("create_character")
    entry = get_object_or_404(InventoryItem.objects.select_related("item"), id=entry_id, character=character)
    if entry.item.slot in ("misc", "material"):
        messages.warning(request, "This item is not equippable.")
        return redirect("inventory")

    if entry.equipped:
        entry.equipped = False
        entry.save(update_fields=["equipped"])
    else:
        character.inventory.filter(equipped=True, item__slot=entry.item.slot).exclude(pk=entry.pk).update(equipped=False)
        entry.equipped = True
        entry.save(update_fields=["equipped"])
    return redirect("inventory")


def city_guard(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")

    pending_gold, pending_resources, elapsed = character.guard_pending_rewards()
    total_seconds = character.guard_total_seconds + elapsed
    return render(
        request,
        "game/guard.html",
        context(
            request,
            character,
            pending_gold=pending_gold,
            pending_resources=pending_resources,
            current_shift_duration=format_duration(elapsed),
            total_guard_duration=format_duration(total_seconds),
        ),
    )


@require_POST
def guard_start(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")

    if character.start_guard_duty():
        messages.success(request, "City Guard duty started. Return whenever you want; there is no fixed shift length.")
    else:
        messages.warning(request, "You are already on City Guard duty.")
    return redirect("city_guard")


@require_POST
def guard_stop(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")

    if not character.guard_active:
        messages.warning(request, "No City Guard shift is currently active.")
        return redirect("city_guard")

    gold, resources, elapsed = character.stop_guard_duty()
    if gold:
        add_season_progress(character, commerce=gold)
    messages.success(
        request,
        f"Guard duty ended after {format_duration(elapsed)}. Collected {gold} gold and {resources} supplies. Partial progress was saved.",
    )
    return redirect("city_guard")


def explore(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")

    if character.guard_active:
        messages.warning(request, "End City Guard duty before returning to dungeon exploration.")
        return redirect("city_guard")

    floor = current_floor(character)
    discover_floor(character, floor)
    enemy, is_boss = floor_encounter(character)
    if not enemy:
        messages.warning(request, "No encounter is configured for this floor yet.")
        return redirect("home")

    discover_enemy(character, enemy)
    result = None
    if request.method == "POST":
        result = resolve_encounter(character, enemy)
        if result.victory:
            if is_boss:
                messages.success(request, f"Boss defeated. Floor {character.floor} is now open.")
            else:
                messages.success(request, f"{enemy.name} defeated.")
        else:
            messages.error(request, f"{character.name} was defeated.")
        character.refresh_from_db()

    return render(
        request,
        "game/explore.html",
        context(request, character, enemy=enemy, result=result, encounter_floor=floor, is_boss=is_boss),
    )


def workshop(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")
    recipes = CraftingRecipe.objects.filter(enabled=True, output_item__unlock_floor__lte=character.floor).select_related("output_item")
    return render(request, "game/workshop.html", context(request, character, recipes=recipes))


@require_POST
def craft_recipe(request, recipe_id):
    character = get_character(request)
    if not character:
        return redirect("create_character")
    if character.guard_active:
        messages.warning(request, "End City Guard duty before using the workshop.")
        return redirect("city_guard")

    recipe = get_object_or_404(
        CraftingRecipe.objects.select_related("output_item"),
        id=recipe_id,
        enabled=True,
        output_item__unlock_floor__lte=character.floor,
    )
    if character.guard_resources < recipe.supply_cost or character.gold < recipe.gold_cost:
        messages.error(request, "You do not have the resources required for this recipe.")
        return redirect("workshop")

    character.guard_resources -= recipe.supply_cost
    character.gold -= recipe.gold_cost
    character.crafting_xp += recipe.xp_reward
    character.save(update_fields=["guard_resources", "gold", "crafting_xp", "updated_at"])

    add_item(character, recipe.output_item, quantity=recipe.output_quantity, floor_number=character.floor)
    add_season_progress(character, crafting=recipe.xp_reward)
    discover_item(character, recipe.output_item)
    messages.success(
        request,
        f"Crafted {recipe.output_quantity}× {recipe.output_item.name}. +{recipe.xp_reward} crafting XP.",
    )
    return redirect("workshop")


def codex(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")

    enemy_total = character.codex_discoveries.model.objects.model.Enemy.objects.filter(enabled=True).count() if False else None
    from .models import Enemy
    enemy_total = Enemy.objects.filter(enabled=True).count()
    item_total = Item.objects.count()
    floor_total = TowerFloor.objects.count()
    discoveries = CodexDiscovery.objects.filter(character=character)
    enemy_entries = discoveries.filter(entry_type="enemy")
    item_entries = discoveries.filter(entry_type="item")
    floor_entries = discoveries.filter(entry_type="floor")
    return render(
        request,
        "game/codex.html",
        context(
            request,
            character,
            enemy_entries=enemy_entries,
            item_entries=item_entries,
            floor_entries=floor_entries,
            enemy_total=enemy_total,
            item_total=item_total,
            floor_total=floor_total,
            total_entries=enemy_total + item_total + floor_total,
            discovered_entries=discoveries.count(),
            completion=character.codex_completion,
        ),
    )


def community(request):
    character = get_character(request)
    season = get_active_season()
    if request.user.is_authenticated and character and season:
        get_season_progress(character, season)

    standings = build_standings(season) if season else []
    own_row = None
    if character:
        own_row = next((row for row in standings if row["character_id"] == character.id), None)

    return render(
        request,
        "game/community.html",
        context(
            request,
            character,
            season=season,
            standings=standings,
            own_row=own_row,
        ),
    )


def _discord_redirect_uri(request):
    if settings.DISCORD_REDIRECT_URI:
        return settings.DISCORD_REDIRECT_URI
    return request.build_absolute_uri(reverse("discord_callback"))


def discord_login(request):
    if not discord_configured():
        messages.error(request, "Discord login is not configured on this SomRPG server yet.")
        return redirect("community")

    state = secrets.token_urlsafe(32)
    request.session["discord_oauth_state"] = state
    params = {
        "client_id": settings.DISCORD_CLIENT_ID,
        "redirect_uri": _discord_redirect_uri(request),
        "response_type": "code",
        "scope": "identify",
        "state": state,
        "prompt": "none",
    }
    return redirect(f"{DISCORD_AUTHORIZE_URL}?{urlencode(params)}")


def discord_callback(request):
    expected_state = request.session.pop("discord_oauth_state", None)
    state = request.GET.get("state")
    code = request.GET.get("code")
    if not expected_state or not state or not secrets.compare_digest(expected_state, state) or not code:
        messages.error(request, "Discord authentication could not be validated.")
        return redirect("community")

    redirect_uri = _discord_redirect_uri(request)
    try:
        token_response = requests.post(
            DISCORD_TOKEN_URL,
            data={
                "client_id": settings.DISCORD_CLIENT_ID,
                "client_secret": settings.DISCORD_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
        token_response.raise_for_status()
        access_token = token_response.json()["access_token"]
        user_response = requests.get(
            DISCORD_USER_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        user_response.raise_for_status()
        discord_user = user_response.json()
    except (requests.RequestException, KeyError, ValueError):
        messages.error(request, "Discord authentication failed. Please try again.")
        return redirect("community")

    discord_id = str(discord_user["id"])
    profile = DiscordProfile.objects.filter(discord_id=discord_id).select_related("user").first()
    if profile:
        user = profile.user
    else:
        user = User.objects.create_user(username=f"discord_{discord_id}")
        profile = DiscordProfile(user=user, discord_id=discord_id)

    profile.username = discord_user.get("username", "Discord user")
    profile.global_name = discord_user.get("global_name") or ""
    profile.avatar = discord_user.get("avatar") or ""
    profile.save()

    auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")

    if not Character.objects.filter(user=user).exists():
        owned_exists = Character.objects.filter(user__isnull=False).exists()
        unowned = Character.objects.filter(user__isnull=True)
        if not owned_exists and unowned.count() == 1:
            legacy_character = unowned.first()
            legacy_character.user = user
            legacy_character.save(update_fields=["user", "updated_at"])

    character = Character.objects.filter(user=user).first()
    if character:
        get_season_progress(character)
    messages.success(request, f"Connected as {profile.display_name}.")
    return redirect("community")


@require_POST
def discord_logout(request):
    auth_logout(request)
    messages.success(request, "Discord account disconnected from this session.")
    return redirect("community")
