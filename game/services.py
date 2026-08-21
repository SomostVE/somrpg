import random
from dataclasses import dataclass
from .models import Character, Enemy, InventoryItem


@dataclass
class CombatResult:
    victory: bool
    enemy: Enemy
    rounds: list[str]
    xp: int = 0
    gold: int = 0
    loot_name: str | None = None
    levels_gained: int = 0


def resolve_encounter(character: Character, enemy: Enemy) -> CombatResult:
    player_hp, enemy_hp = character.max_hp, enemy.max_hp
    rounds = []
    for n in range(1, 51):
        damage = max(1, character.total_attack - enemy.defense + random.randint(-1, 1))
        enemy_hp = max(0, enemy_hp - damage)
        rounds.append(f"Round {n}: {character.name} deals {damage} damage.")
        if enemy_hp <= 0: break
        damage = max(1, enemy.attack - character.total_defense + random.randint(-1, 1))
        player_hp = max(0, player_hp - damage)
        rounds.append(f"{enemy.name} deals {damage} damage.")
        if player_hp <= 0: return CombatResult(False, enemy, rounds)
    if enemy_hp > 0: return CombatResult(False, enemy, rounds)

    gold = random.randint(enemy.gold_min, max(enemy.gold_min, enemy.gold_max))
    levels = character.grant_xp(enemy.xp_reward)
    character.gold += gold
    character.floor += 1
    character.save()
    loot_name = None
    if enemy.loot and random.randint(1, 100) <= enemy.loot_chance:
        entry, created = InventoryItem.objects.get_or_create(character=character, item=enemy.loot, defaults={"quantity": 1})
        if not created:
            entry.quantity += 1
            entry.save(update_fields=["quantity"])
        loot_name = enemy.loot.name
    return CombatResult(True, enemy, rounds, enemy.xp_reward, gold, loot_name, levels)
