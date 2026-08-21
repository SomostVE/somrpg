import random
from datetime import timedelta

from django.utils import timezone

from game.models import Character, InventoryItem, Item
from game.services import add_season_progress, discover_item

from .models import (
    Achievement,
    AchievementUnlock,
    AdventureTemplate,
    ArenaBattle,
    BossContribution,
    BrowserProfile,
    CharacterCompanion,
    CompanionSpecies,
    DailyActivity,
    EventBoss,
    EventDungeon,
    EventDungeonProgress,
    GearEnhancement,
    Guild,
    GuildMembership,
    Stronghold,
)


ARENA_COOLDOWN = timedelta(minutes=10)


def get_profile(character):
    return BrowserProfile.objects.get_or_create(character=character)[0]


def record_daily(character, **increments):
    daily = DailyActivity.objects.get_or_create(character=character, date=timezone.localdate())[0]
    changed = []
    for field, amount in increments.items():
        if amount and hasattr(daily, field):
            setattr(daily, field, getattr(daily, field) + int(amount))
            changed.append(field)
    if changed:
        daily.save(update_fields=changed)
    return daily


def guild_reward_multipliers(character):
    membership = getattr(character, "classic_guild_membership", None)
    if not membership:
        return 1.0, 1.0
    guild = membership.guild
    return (
        1.0 + guild.instructor_level * 0.02 + guild.raid_level * 0.01,
        1.0 + guild.treasure_level * 0.02,
    )


def classic_combat_bonus(character):
    attack = 0
    defense = 0
    companion = character.classic_companions.filter(active=True).select_related("species").first()
    if companion:
        attack += companion.attack_bonus
        defense += companion.defense_bonus

    for entry in character.inventory.filter(equipped=True):
        try:
            enhancement = entry.classic_enhancement
        except GearEnhancement.DoesNotExist:
            continue
        attack += enhancement.attack_bonus
        defense += enhancement.defense_bonus
    return attack, defense


def available_adventures(character):
    profile = get_profile(character)
    profile.refresh_energy()
    templates = list(AdventureTemplate.objects.filter(enabled=True).order_by("difficulty", "id"))
    if len(templates) <= 3:
        return templates
    rng = random.Random(f"{character.pk}:{timezone.localdate().isoformat()}")
    return rng.sample(templates, 3)


def complete_adventure(character, adventure):
    profile = get_profile(character)
    ok, cost = profile.spend_energy(adventure.energy_cost)
    if not ok:
        return False, {"cost": cost}

    xp_mult, gold_mult = guild_reward_multipliers(character)
    xp = int((adventure.xp_reward + random.randint(0, adventure.difficulty * 2)) * xp_mult)
    gold = int((adventure.gold_reward + random.randint(0, adventure.difficulty)) * gold_mult)
    supplies = adventure.supply_reward + (1 if random.randint(1, 100) <= 20 else 0)

    levels = character.grant_xp(xp)
    character.gold += gold
    character.total_gold_earned += gold
    character.guard_resources += supplies
    character.save()
    add_season_progress(character, commerce=gold)
    record_daily(character, adventures=1)
    check_achievements(character)
    return True, {"cost": cost, "xp": xp, "gold": gold, "supplies": supplies, "levels": levels}


def arena_ready(character):
    profile = get_profile(character)
    if not profile.arena_last_fight_at:
        return True, 0
    remaining = ARENA_COOLDOWN - (timezone.now() - profile.arena_last_fight_at)
    seconds = max(0, int(remaining.total_seconds()))
    return seconds <= 0, seconds


def arena_opponents(character):
    qs = Character.objects.exclude(pk=character.pk)
    if character.user_id:
        qs = qs.filter(user__isnull=False)
    return list(qs.order_by("level", "id")[:5])


def resolve_arena(character, opponent):
    profile = get_profile(character)
    opponent_profile = get_profile(opponent)
    ready, wait = arena_ready(character)
    if not ready:
        return None, wait

    atk_bonus, def_bonus = classic_combat_bonus(character)
    o_atk_bonus, o_def_bonus = classic_combat_bonus(opponent)
    attacker_power = (character.total_attack + atk_bonus) * 2 + character.total_defense + def_bonus + character.level * 2 + random.randint(0, 12)
    defender_power = (opponent.total_attack + o_atk_bonus) * 2 + opponent.total_defense + o_def_bonus + opponent.level * 2 + random.randint(0, 12)

    winner = character if attacker_power >= defender_power else opponent
    delta = 10
    if winner == character:
        profile.honor += delta
        profile.arena_wins += 1
        profile.arena_win_streak += 1
        opponent_profile.honor = max(0, opponent_profile.honor - delta)
        character.gold += 2
        character.total_gold_earned += 2
        character.save(update_fields=["gold", "total_gold_earned", "updated_at"])
        add_season_progress(character, commerce=2)
        record_daily(character, arena_wins=1)
    else:
        profile.honor = max(0, profile.honor - delta)
        profile.arena_losses += 1
        profile.arena_win_streak = 0
        opponent_profile.honor += delta

    profile.arena_last_fight_at = timezone.now()
    profile.save()
    opponent_profile.save()
    ArenaBattle.objects.create(attacker=character, defender=opponent, winner=winner, honor_delta=delta)
    check_achievements(character)
    return winner == character, 0


def train_attribute(character, attribute):
    if attribute not in ("attack", "defense", "max_hp"):
        return False, 0
    current = getattr(character, attribute)
    scale = current // (5 if attribute == "max_hp" else 1)
    cost = max(5, 5 + scale * 2)
    if character.gold < cost:
        return False, cost
    character.gold -= cost
    if attribute == "max_hp":
        character.max_hp += 5
    else:
        setattr(character, attribute, current + 1)
    character.save()
    check_achievements(character)
    return True, cost


def mount_options():
    return [
        {"tier": 1, "name": "Courier Horse", "discount": 10, "cost": 60, "days": 7},
        {"tier": 2, "name": "War Elk", "discount": 20, "cost": 150, "days": 7},
        {"tier": 3, "name": "Night Gryphon", "discount": 30, "cost": 320, "days": 7},
    ]


def buy_mount(character, tier):
    profile = get_profile(character)
    option = next((x for x in mount_options() if x["tier"] == tier), None)
    if not option or character.gold < option["cost"]:
        return False, option
    character.gold -= option["cost"]
    character.save(update_fields=["gold", "updated_at"])
    profile.mount_tier = tier
    profile.mount_expires_at = timezone.now() + timedelta(days=option["days"])
    profile.save(update_fields=["mount_tier", "mount_expires_at"])
    return True, option


def shop_items(character):
    profile = get_profile(character)
    items = list(Item.objects.order_by("rarity", "name"))
    rng = random.Random(f"shop:{character.pk}:{timezone.localdate()}:{profile.aura}")
    if len(items) > 6:
        items = rng.sample(items, 6)
    base_prices = {"common": 8, "uncommon": 20, "rare": 45, "epic": 100, "legendary": 220}
    return [{"item": item, "price": max(1, base_prices.get(item.rarity, 10) - min(profile.aura, 20))} for item in items]


def buy_shop_item(character, item):
    offer = next((x for x in shop_items(character) if x["item"].pk == item.pk), None)
    if not offer or character.gold < offer["price"]:
        return False, offer
    character.gold -= offer["price"]
    character.save(update_fields=["gold", "updated_at"])
    entry, created = InventoryItem.objects.get_or_create(character=character, item=item, defaults={"quantity": 1})
    if not created:
        entry.quantity += 1
        entry.save(update_fields=["quantity"])
    discover_item(character, item)
    return True, offer


def salvage_item(character, entry):
    if entry.equipped or entry.quantity <= 0:
        return False, 0
    supplies = {"common": 1, "uncommon": 2, "rare": 4, "epic": 8, "legendary": 15}.get(entry.item.rarity, 1)
    character.guard_resources += supplies
    character.save(update_fields=["guard_resources", "updated_at"])
    entry.quantity -= 1
    if entry.quantity:
        entry.save(update_fields=["quantity"])
    else:
        entry.delete()
    return True, supplies


def upgrade_item(character, entry):
    enhancement, _ = GearEnhancement.objects.get_or_create(inventory_item=entry)
    gold_cost = 5 + enhancement.upgrade_level * 5
    supply_cost = 1 + enhancement.upgrade_level
    if character.gold < gold_cost or character.guard_resources < supply_cost:
        return False, (gold_cost, supply_cost)
    character.gold -= gold_cost
    character.guard_resources -= supply_cost
    character.save(update_fields=["gold", "guard_resources", "updated_at"])
    enhancement.upgrade_level += 1
    enhancement.save(update_fields=["upgrade_level"])
    return True, (gold_cost, supply_cost)


def enchant_item(character, entry, enchantment):
    enhancement, _ = GearEnhancement.objects.get_or_create(inventory_item=entry)
    if character.gold < enchantment.gold_cost:
        return False
    character.gold -= enchantment.gold_cost
    character.save(update_fields=["gold", "updated_at"])
    enhancement.enchantment = enchantment
    enhancement.save(update_fields=["enchantment"])
    return True


def sacrifice_item(character, entry):
    if entry.equipped or entry.quantity <= 0:
        return False, 0
    profile = get_profile(character)
    gain = {"common": 1, "uncommon": 2, "rare": 4, "epic": 7, "legendary": 12}.get(entry.item.rarity, 1)
    profile.aura += gain
    profile.save(update_fields=["aura"])
    entry.quantity -= 1
    if entry.quantity:
        entry.save(update_fields=["quantity"])
    else:
        entry.delete()
    check_achievements(character)
    return True, gain


def get_stronghold(character):
    return Stronghold.objects.get_or_create(character=character)[0]


def collect_stronghold(character):
    stronghold = get_stronghold(character)
    now = timezone.now()
    hours = min(24, max(0, int((now - stronghold.last_collected_at).total_seconds())) // 3600)
    if not hours:
        return stronghold, 0, 0, 0
    wood = hours * stronghold.lumber_level * 2
    stone = hours * stronghold.quarry_level
    souls = hours * stronghold.extractor_level if stronghold.underworld_level else 0
    stronghold.wood += wood
    stronghold.stone += stone
    stronghold.souls += souls
    stronghold.last_collected_at = now
    stronghold.save()
    return stronghold, wood, stone, souls


def upgrade_stronghold(character, building):
    stronghold = get_stronghold(character)
    fields = {
        "fortress": "fortress_level",
        "lumber": "lumber_level",
        "quarry": "quarry_level",
        "underworld": "underworld_level",
        "extractor": "extractor_level",
    }
    field = fields.get(building)
    if not field:
        return False, None
    level = getattr(stronghold, field)
    wood_cost = 20 + level * 15
    stone_cost = 10 + level * 10
    if stronghold.wood < wood_cost or stronghold.stone < stone_cost:
        return False, (wood_cost, stone_cost)
    stronghold.wood -= wood_cost
    stronghold.stone -= stone_cost
    setattr(stronghold, field, level + 1)
    stronghold.save()
    return True, (wood_cost, stone_cost)


def recruit_companion(character, species):
    if character.guard_resources < species.supply_cost:
        return False
    _, created = CharacterCompanion.objects.get_or_create(character=character, species=species)
    if not created:
        return False
    character.guard_resources -= species.supply_cost
    character.save(update_fields=["guard_resources", "updated_at"])
    return True


def activate_companion(character, companion):
    CharacterCompanion.objects.filter(character=character, active=True).update(active=False)
    companion.active = True
    companion.save(update_fields=["active"])


def train_companion(character, companion):
    cost = companion.level * 3
    if character.guard_resources < cost:
        return False, cost
    character.guard_resources -= cost
    character.save(update_fields=["guard_resources", "updated_at"])
    companion.level += 1
    companion.save(update_fields=["level"])
    return True, cost


def create_guild(character, name):
    if hasattr(character, "classic_guild_membership") or character.gold < 50:
        return None
    guild = Guild.objects.create(name=name, owner=character)
    GuildMembership.objects.create(guild=guild, character=character, role="leader")
    character.gold -= 50
    character.save(update_fields=["gold", "updated_at"])
    return guild


def join_guild(character, guild):
    if hasattr(character, "classic_guild_membership"):
        return False
    GuildMembership.objects.create(guild=guild, character=character)
    return True


def donate_guild(character, amount):
    membership = getattr(character, "classic_guild_membership", None)
    amount = max(0, int(amount))
    if not membership or amount <= 0 or character.gold < amount:
        return False
    character.gold -= amount
    membership.guild.treasury_gold += amount
    membership.contributed_gold += amount
    character.save(update_fields=["gold", "updated_at"])
    membership.guild.save(update_fields=["treasury_gold"])
    membership.save(update_fields=["contributed_gold"])
    return True


def upgrade_guild(character, upgrade):
    membership = getattr(character, "classic_guild_membership", None)
    if not membership or membership.role not in ("leader", "officer"):
        return False, None
    field = {"instructor": "instructor_level", "treasure": "treasure_level"}.get(upgrade)
    if not field:
        return False, None
    guild = membership.guild
    level = getattr(guild, field)
    cost = 100 + level * 100
    if guild.treasury_gold < cost:
        return False, cost
    guild.treasury_gold -= cost
    setattr(guild, field, level + 1)
    guild.save()
    return True, cost


def guild_raid(character):
    membership = getattr(character, "classic_guild_membership", None)
    if not membership or membership.role not in ("leader", "officer"):
        return False, None
    guild = membership.guild
    cost = 200 + guild.raid_level * 150
    if guild.treasury_gold < cost:
        return False, cost
    guild.treasury_gold -= cost
    guild.raid_level += 1
    guild.save(update_fields=["treasury_gold", "raid_level"])
    xp = 10 + guild.raid_level * 5
    for member in guild.memberships.select_related("character"):
        member.character.grant_xp(xp)
        member.character.save()
    return True, xp


def achievement_value(character, key):
    profile = get_profile(character)
    return {
        "level": character.level,
        "dungeon_clears": character.dungeon_clears,
        "gold_earned": character.total_gold_earned,
        "crafting_xp": character.crafting_xp,
        "arena_wins": profile.arena_wins,
        "aura": profile.aura,
        "codex": int(character.codex_completion),
        "guard_hours": character.guard_total_seconds // 3600,
    }.get(key, 0)


def check_achievements(character):
    unlocked = []
    for achievement in Achievement.objects.all():
        if achievement_value(character, achievement.stat_key) < achievement.target:
            continue
        _, created = AchievementUnlock.objects.get_or_create(character=character, achievement=achievement)
        if created:
            unlocked.append(achievement)
    if unlocked:
        reward = sum(x.reward_gold for x in unlocked)
        character.gold += reward
        character.total_gold_earned += reward
        character.save(update_fields=["gold", "total_gold_earned", "updated_at"])
        add_season_progress(character, commerce=reward)
    return unlocked


def daily_state(character):
    profile = get_profile(character)
    daily = DailyActivity.objects.get_or_create(character=character, date=timezone.localdate())[0]
    tasks = [("Adventures", daily.adventures, 3), ("Arena wins", daily.arena_wins, 1), ("Dungeon clears", daily.dungeon_clears, 1)]
    return profile, daily, tasks, all(value >= target for _, value, target in tasks)


def claim_daily_reward(character):
    profile = get_profile(character)
    today = timezone.localdate()
    if profile.daily_claim_date == today:
        return False, 0
    yesterday = today - timedelta(days=1)
    profile.login_streak = profile.login_streak + 1 if profile.daily_claim_date == yesterday else 1
    profile.daily_claim_date = today
    profile.save(update_fields=["login_streak", "daily_claim_date"])
    reward = 20 + min(profile.login_streak, 7) * 3
    character.gold += reward
    character.total_gold_earned += reward
    character.save(update_fields=["gold", "total_gold_earned", "updated_at"])
    add_season_progress(character, commerce=reward)
    return True, reward


def claim_daily_tasks(character):
    _, daily, _, complete = daily_state(character)
    if not complete or daily.task_reward_claimed:
        return False, 0
    daily.task_reward_claimed = True
    daily.save(update_fields=["task_reward_claimed"])
    reward = 35
    character.gold += reward
    character.total_gold_earned += reward
    character.save(update_fields=["gold", "total_gold_earned", "updated_at"])
    add_season_progress(character, commerce=reward)
    return True, reward


def fortune_draw(character):
    profile = get_profile(character)
    today = timezone.localdate()
    if profile.fortune_claim_date == today:
        return False, None
    profile.fortune_claim_date = today
    profile.save(update_fields=["fortune_claim_date"])
    kind = random.choice(["gold", "supplies", "energy", "gold", "supplies"])
    if kind == "gold":
        amount = random.randint(5, 15)
        character.gold += amount
        character.total_gold_earned += amount
        character.save(update_fields=["gold", "total_gold_earned", "updated_at"])
        add_season_progress(character, commerce=amount)
    elif kind == "supplies":
        amount = random.randint(2, 6)
        character.guard_resources += amount
        character.save(update_fields=["guard_resources", "updated_at"])
    else:
        amount = random.randint(5, 15)
        profile.refresh_energy()
        profile.adventure_energy = min(100, profile.adventure_energy + amount)
        profile.save(update_fields=["adventure_energy"])
    return True, (kind, amount)


def active_boss():
    now = timezone.now()
    boss = EventBoss.objects.filter(active=True, starts_at__lte=now, current_hp__gt=0).order_by("-starts_at").first()
    return boss if boss and boss.is_open else None


def hit_boss(character):
    boss = active_boss()
    daily = DailyActivity.objects.get_or_create(character=character, date=timezone.localdate())[0]
    if not boss or daily.boss_hits >= 3:
        return False, boss, 0
    bonus_atk, _ = classic_combat_bonus(character)
    damage = max(1, (character.total_attack + bonus_atk) * 5 + random.randint(0, character.level * 3 + 5))
    actual = min(damage, boss.current_hp)
    boss.current_hp -= actual
    if boss.current_hp <= 0:
        boss.current_hp = 0
        boss.active = False
    boss.save()
    contribution, _ = BossContribution.objects.get_or_create(boss=boss, character=character)
    contribution.damage += actual
    contribution.save(update_fields=["damage"])
    daily.boss_hits += 1
    daily.save(update_fields=["boss_hits"])
    reward = max(1, actual // 10)
    character.gold += reward
    character.total_gold_earned += reward
    character.save(update_fields=["gold", "total_gold_earned", "updated_at"])
    add_season_progress(character, commerce=reward)
    return True, boss, actual


def active_event_dungeon():
    now = timezone.now()
    dungeon = EventDungeon.objects.filter(active=True, starts_at__lte=now).order_by("-starts_at").first()
    return dungeon if dungeon and dungeon.is_open else None


def clear_event_floor(character):
    dungeon = active_event_dungeon()
    if not dungeon:
        return False, None, None
    progress, _ = EventDungeonProgress.objects.get_or_create(dungeon=dungeon, character=character)
    if progress.floor > dungeon.max_floor:
        return False, dungeon, progress
    atk_bonus, def_bonus = classic_combat_bonus(character)
    power = (character.total_attack + atk_bonus) * 2 + character.total_defense + def_bonus + character.level * 3 + random.randint(0, 15)
    enemy_power = 12 + progress.floor * 4 + random.randint(0, 10)
    victory = power >= enemy_power
    if victory:
        difficulty = progress.floor
        progress.floor += 1
        progress.clears += 1
        progress.save(update_fields=["floor", "clears"])
        gold = 4 + difficulty
        character.gold += gold
        character.total_gold_earned += gold
        character.save(update_fields=["gold", "total_gold_earned", "updated_at"])
        add_season_progress(character, commerce=gold)
    return victory, dungeon, progress
