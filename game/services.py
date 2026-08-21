import random
from dataclasses import dataclass

from django.db.models import Q
from django.utils import timezone

from .models import (
    Character,
    CodexDiscovery,
    CommunitySeason,
    Enemy,
    Item,
    SeasonProgress,
    TowerFloor,
)
from .tower import add_item


DUNGEON_COEFFICIENT = 1.0
COMMERCE_COEFFICIENT = 2.0
CRAFTING_COEFFICIENT = 2.0
CODEX_COEFFICIENT = 0.5
TOTAL_COEFFICIENT = DUNGEON_COEFFICIENT + COMMERCE_COEFFICIENT + CRAFTING_COEFFICIENT + CODEX_COEFFICIENT


@dataclass
class CombatResult:
    victory: bool
    enemy: Enemy
    rounds: list[str]
    xp: int = 0
    gold: int = 0
    loot_name: str | None = None
    levels_gained: int = 0
    unlocked_floor: int | None = None
    inhabitants_joined: int = 0


def get_active_season():
    now = timezone.now()
    return (
        CommunitySeason.objects.filter(active=True, starts_at__lte=now)
        .filter(Q(ends_at__isnull=True) | Q(ends_at__gt=now))
        .order_by("-starts_at")
        .first()
    )


def get_season_progress(character: Character, season=None):
    season = season or get_active_season()
    if not season:
        return None
    progress, _ = SeasonProgress.objects.get_or_create(season=season, character=character)
    return progress


def add_season_progress(character: Character, dungeon=0, commerce=0, crafting=0):
    progress = get_season_progress(character)
    if not progress:
        return
    changed = []
    if dungeon:
        progress.dungeon_clears += dungeon
        changed.append("dungeon_clears")
    if commerce:
        progress.commerce_gold += commerce
        changed.append("commerce_gold")
    if crafting:
        progress.crafting_xp += crafting
        changed.append("crafting_xp")
    if changed:
        changed.append("updated_at")
        progress.save(update_fields=changed)


def discover(character: Character, entry_type: str, entry_key, label: str):
    discovery, created = CodexDiscovery.objects.get_or_create(
        character=character,
        entry_type=entry_type,
        entry_key=str(entry_key),
        defaults={"label": label},
    )
    if not created and discovery.label != label:
        discovery.label = label
        discovery.save(update_fields=["label"])
    return created


def discover_enemy(character: Character, enemy: Enemy):
    return discover(character, "enemy", enemy.pk, enemy.name)


def discover_item(character: Character, item: Item):
    return discover(character, "item", item.pk, item.name)


def discover_floor(character: Character, floor: TowerFloor | None):
    if not floor:
        return False
    return discover(character, "floor", floor.floor_number, f"Sector {floor.floor_number} — {floor.name}")


def resolve_encounter(character: Character, enemy: Enemy, floor_number=None) -> CombatResult:
    from classic.colony import colony_bonuses, recruit_inhabitants
    from classic.services import classic_combat_bonus

    defeated_floor = floor_number or character.floor
    frontier_clear = defeated_floor == character.floor
    extra_attack, extra_defense = classic_combat_bonus(character)
    colony = colony_bonuses(character)
    player_hp, enemy_hp = character.combat_max_hp, enemy.max_hp
    rounds = []
    if enemy.is_boss:
        rounds.append(f"BOSS GATE: {enemy.name} blocks Sector {defeated_floor}.")

    for n in range(1, 51):
        damage = max(1, character.total_attack + extra_attack + colony["damage"] - enemy.defense + random.randint(-1, 1))
        enemy_hp = max(0, enemy_hp - damage)
        rounds.append(f"Round {n}: {character.name} deals {damage} damage.")
        if enemy_hp <= 0:
            break
        damage = max(1, enemy.attack - character.total_defense - extra_defense + random.randint(-1, 1))
        player_hp = max(0, player_hp - damage)
        rounds.append(f"{enemy.name} deals {damage} damage.")
        if player_hp <= 0:
            return CombatResult(False, enemy, rounds)
    if enemy_hp > 0:
        return CombatResult(False, enemy, rounds)

    from classic.services import guild_reward_multipliers

    xp_multiplier, gold_multiplier = guild_reward_multipliers(character)
    xp_reward = int(enemy.xp_reward * xp_multiplier)
    gold = int(random.randint(enemy.gold_min, max(enemy.gold_min, enemy.gold_max)) * gold_multiplier * colony["gold_multiplier"])
    levels = character.grant_xp(xp_reward)
    character.gold += gold
    character.total_gold_earned += gold
    character.dungeon_clears += 1

    unlocked_floor = None
    if frontier_clear:
        next_floor = TowerFloor.objects.filter(floor_number__gt=defeated_floor).order_by("floor_number").first()
        if next_floor:
            character.floor = next_floor.floor_number
            unlocked_floor = next_floor.floor_number

    character.save()
    add_season_progress(character, dungeon=1 if unlocked_floor else 0, commerce=gold)

    loot_name = None
    loot_chance = min(100, enemy.loot_chance + colony["loot_bonus"])
    if enemy.loot and random.randint(1, 100) <= loot_chance:
        entry, _ = add_item(character, enemy.loot, floor_number=defeated_floor)
        discover_item(character, enemy.loot)
        loot_name = entry.display_name

    if unlocked_floor:
        discover_floor(character, TowerFloor.objects.filter(floor_number=unlocked_floor).first())

    inhabitants_joined = recruit_inhabitants(character, 3 if enemy.is_boss and frontier_clear else (2 if unlocked_floor else 1))

    from classic.services import check_achievements, record_daily

    record_daily(character, dungeon_clears=1)
    check_achievements(character)

    return CombatResult(
        True,
        enemy,
        rounds,
        xp=xp_reward,
        gold=gold,
        loot_name=loot_name,
        levels_gained=levels,
        unlocked_floor=unlocked_floor,
        inhabitants_joined=inhabitants_joined,
    )


def _normalized(value, maximum):
    if maximum <= 0:
        return 0.0
    return value * 100.0 / maximum


def _dense_ranks(rows, key):
    ordered = sorted(rows, key=lambda row: (-row[key], row["display_name"].lower()))
    result = {}
    previous = None
    rank = 0
    for index, row in enumerate(ordered, start=1):
        value = row[key]
        if previous is None or value != previous:
            rank = index
            previous = value
        result[row["character_id"]] = rank
    return result


def build_standings(season: CommunitySeason):
    progresses = list(
        SeasonProgress.objects.filter(season=season, character__user__isnull=False)
        .select_related("character", "character__user", "character__user__discord_profile")
    )

    rows = []
    for progress in progresses:
        character = progress.character
        profile = getattr(character.user, "discord_profile", None)
        rows.append(
            {
                "character_id": character.id,
                "character": character,
                "display_name": profile.display_name if profile else character.name,
                "dungeon_value": progress.dungeon_clears,
                "commerce_value": progress.commerce_gold,
                "crafting_value": progress.crafting_xp,
                "codex_value": character.codex_completion,
            }
        )

    max_dungeon = max((row["dungeon_value"] for row in rows), default=0)
    max_commerce = max((row["commerce_value"] for row in rows), default=0)
    max_crafting = max((row["crafting_value"] for row in rows), default=0)

    for row in rows:
        row["dungeon_score"] = _normalized(row["dungeon_value"], max_dungeon)
        row["commerce_score"] = _normalized(row["commerce_value"], max_commerce)
        row["crafting_score"] = _normalized(row["crafting_value"], max_crafting)
        row["codex_score"] = row["codex_value"]
        row["global_score"] = (
            row["dungeon_score"] * DUNGEON_COEFFICIENT
            + row["commerce_score"] * COMMERCE_COEFFICIENT
            + row["crafting_score"] * CRAFTING_COEFFICIENT
            + row["codex_score"] * CODEX_COEFFICIENT
        ) / TOTAL_COEFFICIENT

    dungeon_ranks = _dense_ranks(rows, "dungeon_value")
    commerce_ranks = _dense_ranks(rows, "commerce_value")
    crafting_ranks = _dense_ranks(rows, "crafting_value")
    codex_ranks = _dense_ranks(rows, "codex_value")

    rows.sort(key=lambda row: (-row["global_score"], row["display_name"].lower()))
    previous_score = None
    global_rank = 0
    for index, row in enumerate(rows, start=1):
        rounded = round(row["global_score"], 6)
        if previous_score is None or rounded != previous_score:
            global_rank = index
            previous_score = rounded
        row["global_rank"] = global_rank
        row["dungeon_rank"] = dungeon_ranks[row["character_id"]]
        row["commerce_rank"] = commerce_ranks[row["character_id"]]
        row["crafting_rank"] = crafting_ranks[row["character_id"]]
        row["codex_rank"] = codex_ranks[row["character_id"]]

    return rows
