import random

from django.db.models import Q

from .models import Enemy, FloorShopOffer, InventoryItem, TowerFloor


AFFIXES = [
    (1, "Fine", 1, 0, 38),
    (1, "Guarded", 0, 1, 38),
    (5, "Balanced", 1, 1, 30),
    (10, "Keen", 2, 0, 24),
    (10, "Reinforced", 0, 2, 24),
    (15, "Ancient", 2, 2, 16),
    (20, "Starforged", 3, 2, 10),
]


def tower_floor(number):
    return TowerFloor.objects.filter(floor_number=number).first()


def current_floor(character, floor_number=None):
    return tower_floor(floor_number or character.floor)


def floor_encounter(character, floor_number=None):
    number = floor_number or character.floor
    floor = tower_floor(number)

    # A boss only blocks the current progression frontier. Once a higher floor
    # is unlocked, returning to that boss floor becomes a normal replay visit.
    if floor and number == character.floor and hasattr(floor, "boss_gate"):
        return floor.boss_gate.enemy, True

    qs = Enemy.objects.filter(enabled=True, is_boss=False, floor_min__lte=number).filter(
        Q(floor_max__isnull=True) | Q(floor_max__gte=number)
    )
    enemy = qs.order_by("-floor_min", "id").first()

    # Boss-only floors may have no regular enemy explicitly assigned. Replays
    # fall back to the nearest earlier non-boss encounter rather than becoming
    # inaccessible after the boss has been cleared.
    if enemy is None:
        enemy = (
            Enemy.objects.filter(enabled=True, is_boss=False, floor_min__lte=number)
            .order_by("-floor_min", "id")
            .first()
        )
    return enemy, False


def available_shop_offers(character, floor_number=None):
    number = floor_number or character.floor
    return FloorShopOffer.objects.filter(enabled=True, unlock_floor__lte=number).select_related("item")


def newly_unlocked_offers(character, floor_number=None):
    number = floor_number or character.floor
    return FloorShopOffer.objects.filter(enabled=True, unlock_floor=number).select_related("item")


def roll_affix(entry: InventoryItem, floor_number: int, force=False):
    if entry.item.slot in ("misc", "material"):
        return entry
    if entry.affix_name and not force:
        return entry
    if not force and random.randint(1, 100) > 45:
        return entry

    eligible = [row for row in AFFIXES if row[0] <= floor_number]
    if not eligible:
        return entry

    weighted = []
    for row in eligible:
        weighted.extend([row] * row[4])
    _, name, attack, defense, _ = random.choice(weighted)
    entry.affix_name = name
    entry.affix_attack_bonus = attack
    entry.affix_defense_bonus = defense
    entry.save(update_fields=["affix_name", "affix_attack_bonus", "affix_defense_bonus"])
    return entry


def add_item(character, item, quantity=1, floor_number=None, affix_chance=True):
    entry, created = InventoryItem.objects.get_or_create(
        character=character,
        item=item,
        defaults={"quantity": quantity},
    )
    if not created:
        entry.quantity += quantity
        entry.save(update_fields=["quantity"])
    if created and affix_chance:
        roll_affix(entry, floor_number or character.floor)
    return entry, created


def visible_tower_floors(character, future=2):
    limit = max(character.floor + future, 1)
    return TowerFloor.objects.filter(floor_number__lte=limit).select_related("boss_gate__enemy")
