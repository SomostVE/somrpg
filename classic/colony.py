from datetime import timedelta

from django.utils import timezone

from .models import Colony


BUILDINGS = {
    "treasury": {"base_cost": 80, "population": 5},
    "market": {"base_cost": 70, "population": 5},
    "hunters": {"base_cost": 90, "population": 8},
    "training": {"base_cost": 100, "population": 8},
}


def get_colony(character):
    try:
        return character.colony
    except Colony.DoesNotExist:
        return Colony.objects.get_or_create(character=character)[0]


def colony_bonuses(character, colony=None):
    colony = colony or get_colony(character)
    return {
        "damage": colony.training_level,
        "gold_multiplier": 1.0 + colony.treasury_level * 0.05,
        "loot_bonus": colony.hunters_level * 3,
        "sell_multiplier": min(0.90, 0.50 + colony.market_level * 0.05),
    }


def recruit_inhabitants(character, amount=1):
    if amount <= 0:
        return 0
    colony = get_colony(character)
    colony.inhabitants += int(amount)
    colony.lifetime_recruited += int(amount)
    colony.save(update_fields=["inhabitants", "lifetime_recruited"])
    return int(amount)


def upgrade_quote(colony, building):
    config = BUILDINGS.get(building)
    if not config:
        return None
    level = getattr(colony, f"{building}_level")
    next_level = level + 1
    return {
        "level": level,
        "next_level": next_level,
        "cost": config["base_cost"] * next_level * next_level,
        "population": config["population"] * next_level,
    }


def upgrade_colony(character, building):
    colony = get_colony(character)
    quote = upgrade_quote(colony, building)
    if not quote:
        return False, None
    if character.gold < quote["cost"] or colony.inhabitants < quote["population"]:
        return False, quote
    character.gold -= quote["cost"]
    character.save(update_fields=["gold", "updated_at"])
    field = f"{building}_level"
    setattr(colony, field, quote["next_level"])
    colony.save(update_fields=[field])
    return True, quote


def pending_colony_gold(colony, now=None):
    now = now or timezone.now()
    elapsed = max(0, int((now - colony.last_gold_collected_at).total_seconds()))
    hours = elapsed // 3600
    if not hours:
        return 0, 0
    base_per_hour = max(1, colony.inhabitants // 5)
    amount = hours * base_per_hour * (1 + colony.treasury_level)
    return amount, hours


def collect_colony_gold(character):
    colony = get_colony(character)
    amount, hours = pending_colony_gold(colony)
    if not hours:
        return 0
    colony.last_gold_collected_at += timedelta(hours=hours)
    colony.save(update_fields=["last_gold_collected_at"])
    character.gold += amount
    character.total_gold_earned += amount
    character.save(update_fields=["gold", "total_gold_earned", "updated_at"])
    return amount


def sell_value(character, item):
    bonuses = colony_bonuses(character)
    return max(1, int(item.shop_price * bonuses["sell_multiplier"]))
