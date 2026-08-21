from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from game.models import Character, InventoryItem, Item
from game.views import context, get_character

from .models import Achievement, CharacterCompanion, CompanionSpecies, Enchantment, EventDungeonProgress, Guild
from .services import (
    activate_companion,
    active_boss,
    active_event_dungeon,
    arena_opponents,
    arena_ready,
    available_adventures,
    buy_mount,
    buy_shop_item,
    check_achievements,
    claim_daily_reward,
    claim_daily_tasks,
    clear_event_floor,
    collect_stronghold,
    complete_adventure,
    create_guild,
    daily_state,
    donate_guild,
    enchant_item,
    fortune_draw,
    get_profile,
    guild_raid,
    hit_boss,
    join_guild,
    mount_options,
    recruit_companion,
    resolve_arena,
    sacrifice_item,
    salvage_item,
    shop_items,
    train_attribute,
    train_companion,
    upgrade_guild,
    upgrade_item,
    upgrade_stronghold,
)


def _character(request):
    return get_character(request)


def _back(section="top"):
    return redirect(f"{reverse('classic:town')}#{section}")


def town(request):
    character = _character(request)
    if not character:
        return redirect("create_character")

    profile = get_profile(character)
    profile.refresh_energy()
    check_achievements(character)
    stronghold, wood, stone, souls = collect_stronghold(character)
    if wood or stone or souls:
        messages.success(request, f"Stronghold production collected: +{wood} wood, +{stone} stone, +{souls} souls.")

    membership = getattr(character, "classic_guild_membership", None)
    owned_companions = character.classic_companions.select_related("species")
    owned_species = list(owned_companions.values_list("species_id", flat=True))
    daily_profile, daily, daily_tasks, daily_complete = daily_state(character)

    boss = active_boss()
    boss_contribution = boss.contributions.filter(character=character).first() if boss else None
    event_dungeon = active_event_dungeon()
    event_progress = EventDungeonProgress.objects.filter(dungeon=event_dungeon, character=character).first() if event_dungeon else None

    unlocked = set(character.classic_achievement_unlocks.values_list("achievement_id", flat=True))
    achievement_rows = [{"achievement": achievement, "unlocked": achievement.pk in unlocked} for achievement in Achievement.objects.all()]

    ready, arena_wait = arena_ready(character)
    data = context(
        request,
        character,
        classic_profile=profile,
        adventures=available_adventures(character),
        arena_opponents=arena_opponents(character),
        arena_ready=ready,
        arena_wait=arena_wait,
        market_offers=shop_items(character),
        mounts=mount_options(),
        inventory_entries=character.inventory.select_related("item").all(),
        enchantments=Enchantment.objects.all(),
        stronghold=stronghold,
        companions=owned_companions,
        companion_species=CompanionSpecies.objects.exclude(pk__in=owned_species),
        guild_membership=membership,
        guilds=Guild.objects.order_by("-raid_level", "name")[:30],
        daily=daily,
        daily_tasks=daily_tasks,
        daily_complete=daily_complete,
        achievements=achievement_rows,
        boss=boss,
        boss_contribution=boss_contribution,
        event_dungeon=event_dungeon,
        event_progress=event_progress,
    )
    return render(request, "classic/town.html", data)


@require_POST
def action(request):
    character = _character(request)
    if not character:
        return redirect("create_character")

    action_name = request.POST.get("action", "")
    section = request.POST.get("section", "top")

    if character.guard_active and action_name not in {"daily_reward", "daily_tasks", "fortune"}:
        messages.warning(request, "End City Guard duty before using active town services.")
        return _back("guard")

    if action_name == "adventure":
        from .models import AdventureTemplate
        adventure = get_object_or_404(AdventureTemplate, pk=request.POST.get("id"), enabled=True)
        ok, result = complete_adventure(character, adventure)
        if ok:
            messages.success(request, f"{adventure.name}: +{result['xp']} XP, +{result['gold']} gold, +{result['supplies']} supplies.")
        else:
            messages.error(request, f"Not enough AP. Required: {result['cost']}.")

    elif action_name == "arena":
        opponent = get_object_or_404(Character, pk=request.POST.get("id"))
        if opponent.pk == character.pk:
            messages.error(request, "You cannot challenge yourself.")
        else:
            won, wait = resolve_arena(character, opponent)
            if won is None:
                messages.warning(request, f"Arena cooldown: about {wait // 60 + 1} minute(s).")
            elif won:
                messages.success(request, f"Arena victory over {opponent.name}.")
            else:
                messages.warning(request, f"Arena defeat against {opponent.name}.")

    elif action_name == "train":
        attribute = request.POST.get("attribute", "")
        ok, cost = train_attribute(character, attribute)
        messages.success(request, f"{attribute.replace('_', ' ').title()} improved.") if ok else messages.error(request, f"Training requires {cost} gold.")

    elif action_name == "buy_item":
        item = get_object_or_404(Item, pk=request.POST.get("id"))
        ok, offer = buy_shop_item(character, item)
        messages.success(request, f"Purchased {item.name} for {offer['price']} gold.") if ok else messages.error(request, "Item unavailable or not enough gold.")

    elif action_name == "mount":
        ok, option = buy_mount(character, int(request.POST.get("tier", "0")))
        messages.success(request, f"{option['name']} hired.") if ok else messages.error(request, "Mount unavailable or not enough gold.")

    elif action_name == "salvage":
        entry = get_object_or_404(InventoryItem, pk=request.POST.get("id"), character=character)
        ok, amount = salvage_item(character, entry)
        messages.success(request, f"Dismantled into {amount} supplies.") if ok else messages.error(request, "Equipped items cannot be dismantled.")

    elif action_name == "upgrade_item":
        entry = get_object_or_404(InventoryItem, pk=request.POST.get("id"), character=character)
        ok, costs = upgrade_item(character, entry)
        messages.success(request, "Equipment upgraded.") if ok else messages.error(request, f"Need {costs[0]} gold and {costs[1]} supplies.")

    elif action_name == "enchant":
        entry = get_object_or_404(InventoryItem, pk=request.POST.get("entry"), character=character)
        enchantment = get_object_or_404(Enchantment, pk=request.POST.get("enchantment"))
        messages.success(request, f"Applied {enchantment.name}.") if enchant_item(character, entry, enchantment) else messages.error(request, f"Need {enchantment.gold_cost} gold.")

    elif action_name == "sacrifice":
        entry = get_object_or_404(InventoryItem, pk=request.POST.get("id"), character=character)
        ok, gain = sacrifice_item(character, entry)
        messages.success(request, f"Aura +{gain}.") if ok else messages.error(request, "That item cannot be sacrificed.")

    elif action_name == "stronghold":
        ok, costs = upgrade_stronghold(character, request.POST.get("building", ""))
        messages.success(request, "Stronghold building upgraded.") if ok else messages.error(request, f"Need {costs[0]} wood and {costs[1]} stone." if costs else "Unknown building.")

    elif action_name == "recruit_companion":
        species = get_object_or_404(CompanionSpecies, pk=request.POST.get("id"))
        messages.success(request, f"{species.name} joined you.") if recruit_companion(character, species) else messages.error(request, "Not enough supplies or already recruited.")

    elif action_name == "activate_companion":
        companion = get_object_or_404(CharacterCompanion, pk=request.POST.get("id"), character=character)
        activate_companion(character, companion)
        messages.success(request, f"{companion.species.name} is active.")

    elif action_name == "train_companion":
        companion = get_object_or_404(CharacterCompanion, pk=request.POST.get("id"), character=character)
        ok, cost = train_companion(character, companion)
        messages.success(request, f"{companion.species.name} reached level {companion.level}.") if ok else messages.error(request, f"Need {cost} supplies.")

    elif action_name == "create_guild":
        name = request.POST.get("name", "").strip()[:80]
        try:
            guild = create_guild(character, name) if name else None
        except Exception:
            guild = None
        messages.success(request, f"Guild {guild.name} founded.") if guild else messages.error(request, "Guild creation failed. Cost: 50 gold; name must be unique.")

    elif action_name == "join_guild":
        guild = get_object_or_404(Guild, pk=request.POST.get("id"))
        messages.success(request, f"Joined {guild.name}.") if join_guild(character, guild) else messages.error(request, "You already belong to a guild.")

    elif action_name == "guild_donate":
        try:
            amount = int(request.POST.get("amount", "0"))
        except ValueError:
            amount = 0
        messages.success(request, f"Donated {amount} gold.") if donate_guild(character, amount) else messages.error(request, "Donation failed.")

    elif action_name == "guild_upgrade":
        ok, cost = upgrade_guild(character, request.POST.get("upgrade", ""))
        messages.success(request, "Guild upgrade completed.") if ok else messages.error(request, f"Upgrade unavailable or treasury needs {cost or '?'} gold.")

    elif action_name == "guild_raid":
        ok, value = guild_raid(character)
        messages.success(request, f"Guild raid cleared. Members gained {value} XP.") if ok else messages.error(request, f"Raid unavailable or treasury needs {value or '?'} gold.")

    elif action_name == "daily_reward":
        ok, reward = claim_daily_reward(character)
        messages.success(request, f"Daily reward: +{reward} gold.") if ok else messages.warning(request, "Daily reward already claimed.")

    elif action_name == "daily_tasks":
        ok, reward = claim_daily_tasks(character)
        messages.success(request, f"Checklist reward: +{reward} gold.") if ok else messages.warning(request, "Complete the checklist first, or the reward was already claimed.")

    elif action_name == "fortune":
        ok, reward = fortune_draw(character)
        messages.success(request, f"Fortune Shrine: +{reward[1]} {reward[0]}.") if ok else messages.warning(request, "Fortune Shrine already used today.")

    elif action_name == "boss":
        ok, boss, damage = hit_boss(character)
        messages.success(request, f"Dealt {damage} damage to {boss.name}.") if ok else messages.warning(request, "No active boss or today's three attacks are used.")

    elif action_name == "event_dungeon":
        victory, dungeon, progress = clear_event_floor(character)
        if dungeon is None:
            messages.warning(request, "No event dungeon is active.")
        elif victory:
            messages.success(request, f"Event floor cleared. Next floor: {progress.floor}.")
        else:
            messages.warning(request, "The event floor defeated you.")

    else:
        messages.error(request, "Unknown town command.")

    return _back(section)
