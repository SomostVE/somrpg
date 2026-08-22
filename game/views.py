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
    Enemy,
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
ACTIVE_FLOOR_SESSION_KEY = "somrpg.active_floor"
ACTIVE_CHARACTER_SESSION_KEY = "somrpg.active_character_id"
CHARACTER_LIMIT = 3


def discord_configured():
    return bool(settings.DISCORD_CLIENT_ID and settings.DISCORD_CLIENT_SECRET)


def owned_characters(request):
    if request.user.is_authenticated:
        return Character.objects.filter(user=request.user).order_by("id")
    return Character.objects.filter(user__isnull=True).order_by("id")


def get_character(request):
    characters = owned_characters(request)
    try:
        active_id = int(request.session.get(ACTIVE_CHARACTER_SESSION_KEY, 0))
    except (TypeError, ValueError):
        active_id = 0

    character = characters.filter(pk=active_id).first() if active_id else None
    if character is None:
        character = characters.first()
    if character is not None:
        request.session[ACTIVE_CHARACTER_SESSION_KEY] = character.pk
    return character


def active_floor_number(request, character):
    if not character:
        return 1

    try:
        number = int(request.session.get(ACTIVE_FLOOR_SESSION_KEY, character.floor))
    except (TypeError, ValueError):
        number = character.floor

    if number < 1 or number > character.floor or not TowerFloor.objects.filter(floor_number=number).exists():
        number = character.floor

    request.session[ACTIVE_FLOOR_SESSION_KEY] = number
    return number


def context(request, character, **extra):
    active_floor = active_floor_number(request, character) if character else 1
    floor = current_floor(character, active_floor) if character else None
    return {
        "character": character,
        "version": settings.SOMRPG_VERSION,
        "discord_configured": discord_configured(),
        "discord_profile": getattr(request.user, "discord_profile", None) if request.user.is_authenticated else None,
        "navigation_sections": navigation_for(character) if character else [],
        "active_floor": active_floor,
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
    active_floor = active_floor_number(request, character)
    floor = current_floor(character, active_floor)
    discover_floor(character, floor)
    return render(
        request,
        "game/home.html",
        context(
            request,
            character,
            new_shop_offers=newly_unlocked_offers(character, active_floor),
            floor_boss=getattr(floor, "boss_gate", None) if floor and active_floor == character.floor else None,
        ),
    )


def create_character(request):
    characters = owned_characters(request)
    if characters.count() >= CHARACTER_LIMIT:
        messages.warning(request, f"Character limit reached ({CHARACTER_LIMIT}).")
        return redirect("options")

    form = CharacterCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        character = form.save(commit=False)
        if request.user.is_authenticated:
            character.user = request.user
        character.save()
        request.session[ACTIVE_CHARACTER_SESSION_KEY] = character.pk
        request.session[ACTIVE_FLOOR_SESSION_KEY] = 1
        discover_floor(character, current_floor(character, 1))
        if request.user.is_authenticated:
            get_season_progress(character)
        return redirect("home")

    return render(
        request,
        "game/create_character.html",
        context(request, None, form=form, character_count=characters.count(), character_limit=CHARACTER_LIMIT),
    )


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


@require_POST
def travel_floor(request, floor_number):
    character = get_character(request)
    if not character:
        return redirect("create_character")
    if character.guard_active:
        messages.warning(request, "End City Guard duty first.")
        return redirect("city_guard")

    destination = TowerFloor.objects.filter(floor_number=floor_number).first()
    if not destination or floor_number > character.floor:
        messages.warning(request, "Floor locked.")
        return redirect("tower_map")

    request.session[ACTIVE_FLOOR_SESSION_KEY] = floor_number
    discover_floor(character, destination)
    return_to = request.POST.get("return_to", "tower_map")
    if return_to not in {"tower_map", "home", "floor_shop", "explore"}:
        return_to = "tower_map"
    return redirect(return_to)


def floor_shop(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")
    active_floor = active_floor_number(request, character)
    offers = available_shop_offers(character, active_floor)
    return render(
        request,
        "game/shop.html",
        context(
            request,
            character,
            offers=offers,
            new_offers=offers.filter(unlock_floor=active_floor),
        ),
    )


@require_POST
def buy_floor_shop_item(request, offer_id):
    character = get_character(request)
    if not character:
        return redirect("create_character")
    active_floor = active_floor_number(request, character)
    offer = get_object_or_404(
        FloorShopOffer.objects.select_related("item"),
        id=offer_id,
        enabled=True,
        unlock_floor__lte=active_floor,
    )
    if character.gold < offer.price:
        messages.error(request, "Not enough gold.")
        return redirect("floor_shop")

    character.gold -= offer.price
    character.save(update_fields=["gold", "updated_at"])
    entry, _ = add_item(character, offer.item, floor_number=active_floor)
    discover_item(character, offer.item)
    messages.success(request, f"Purchased {entry.display_name}.")
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
        messages.success(request, "City Guard duty started.")
    else:
        messages.warning(request, "Already on duty.")
    return redirect("city_guard")


@require_POST
def guard_stop(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")

    if not character.guard_active:
        messages.warning(request, "No active guard duty.")
        return redirect("city_guard")

    gold, resources, elapsed = character.stop_guard_duty()
    if gold:
        add_season_progress(character, commerce=gold)
    messages.success(request, f"Guard duty ended: +{gold} gold, +{resources} supplies.")
    return redirect("city_guard")


def explore(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")

    if character.guard_active:
        messages.warning(request, "End City Guard duty first.")
        return redirect("city_guard")

    active_floor = active_floor_number(request, character)
    floor = current_floor(character, active_floor)
    discover_floor(character, floor)
    enemy, is_boss = floor_encounter(character, active_floor)
    if not enemy:
        messages.warning(request, "No encounter configured here.")
        return redirect("home")

    discover_enemy(character, enemy)
    result = None
    if request.method == "POST":
        result = resolve_encounter(character, enemy, active_floor)
        character.refresh_from_db()
        if result.unlocked_floor:
            request.session[ACTIVE_FLOOR_SESSION_KEY] = result.unlocked_floor
        elif not result.victory:
            messages.error(request, f"{character.name} was defeated.")

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
        messages.warning(request, "End City Guard duty first.")
        return redirect("city_guard")

    recipe = get_object_or_404(
        CraftingRecipe.objects.select_related("output_item"),
        id=recipe_id,
        enabled=True,
        output_item__unlock_floor__lte=character.floor,
    )
    if character.guard_resources < recipe.supply_cost or character.gold < recipe.gold_cost:
        messages.error(request, "Not enough resources.")
        return redirect("workshop")

    character.guard_resources -= recipe.supply_cost
    character.gold -= recipe.gold_cost
    character.crafting_xp += recipe.xp_reward
    character.save(update_fields=["guard_resources", "gold", "crafting_xp", "updated_at"])

    add_item(character, recipe.output_item, quantity=recipe.output_quantity, floor_number=character.floor)
    add_season_progress(character, crafting=recipe.xp_reward)
    discover_item(character, recipe.output_item)
    messages.success(request, f"Crafted {recipe.output_quantity}× {recipe.output_item.name}.")
    return redirect("workshop")


def codex(request):
    character = get_character(request)
    if not character:
        return redirect("create_character")

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


def discord_redirect_uri(request):
    if settings.DISCORD_REDIRECT_URI:
        return settings.DISCORD_REDIRECT_URI
    return request.build_absolute_uri(reverse("discord_callback"))


def discord_login(request):
    if not discord_configured():
        messages.error(request, "Discord login is not configured on this SomRPG server yet.")
        return redirect("options")

    state = secrets.token_urlsafe(32)
    request.session["discord_oauth_state"] = state
    params = {
        "client_id": settings.DISCORD_CLIENT_ID,
        "redirect_uri": discord_redirect_uri(request),
        "response_type": "code",
        "scope": "identify",
        "state": state,
    }
    return redirect(f"{DISCORD_AUTHORIZE_URL}?{urlencode(params)}")


def discord_callback(request):
    expected_state = request.session.pop("discord_oauth_state", None)
    state = request.GET.get("state")
    code = request.GET.get("code")
    if not expected_state or not state or not secrets.compare_digest(expected_state, state) or not code:
        messages.error(request, "Discord authentication could not be validated.")
        return redirect("options")

    redirect_uri = discord_redirect_uri(request)
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
        return redirect("options")

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

    local_active_id = request.session.get(ACTIVE_CHARACTER_SESSION_KEY)
    auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")

    user_characters = Character.objects.filter(user=user).order_by("id")
    if not user_characters.exists():
        other_owned_exists = Character.objects.filter(user__isnull=False).exclude(user=user).exists()
        if not other_owned_exists:
            for legacy_character in Character.objects.filter(user__isnull=True).order_by("id")[:CHARACTER_LIMIT]:
                legacy_character.user = user
                legacy_character.save(update_fields=["user", "updated_at"])

    user_characters = Character.objects.filter(user=user).order_by("id")
    character = user_characters.filter(pk=local_active_id).first() if local_active_id else None
    if character is None:
        character = user_characters.first()
    if character:
        request.session[ACTIVE_CHARACTER_SESSION_KEY] = character.pk
        request.session[ACTIVE_FLOOR_SESSION_KEY] = character.floor
        get_season_progress(character)
    messages.success(request, f"Connected as {profile.display_name}.")
    return redirect("options")


@require_POST
def discord_logout(request):
    auth_logout(request)
    messages.success(request, "Discord account disconnected from this session.")
    return redirect("options")
