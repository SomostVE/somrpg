from django.db import models
from django.utils import timezone


GUARD_GOLD_INTERVAL_SECONDS = 10 * 60
GUARD_RESOURCE_INTERVAL_SECONDS = 30 * 60


class Item(models.Model):
    RARITY_CHOICES = [("common", "Common"), ("uncommon", "Uncommon"), ("rare", "Rare"), ("epic", "Epic"), ("legendary", "Legendary")]
    name = models.CharField(max_length=80, unique=True)
    description = models.CharField(max_length=240, blank=True)
    rarity = models.CharField(max_length=16, choices=RARITY_CHOICES, default="common")
    attack_bonus = models.PositiveIntegerField(default=0)
    defense_bonus = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Enemy(models.Model):
    name = models.CharField(max_length=80, unique=True)
    floor_min = models.PositiveIntegerField(default=1)
    max_hp = models.PositiveIntegerField(default=10)
    attack = models.PositiveIntegerField(default=2)
    defense = models.PositiveIntegerField(default=0)
    xp_reward = models.PositiveIntegerField(default=5)
    gold_min = models.PositiveIntegerField(default=1)
    gold_max = models.PositiveIntegerField(default=3)
    loot = models.ForeignKey(Item, null=True, blank=True, on_delete=models.SET_NULL)
    loot_chance = models.PositiveSmallIntegerField(default=25)
    enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ["floor_min", "name"]

    def __str__(self):
        return self.name


class Character(models.Model):
    name = models.CharField(max_length=40, default="Adventurer")
    level = models.PositiveIntegerField(default=1)
    xp = models.PositiveIntegerField(default=0)
    gold = models.PositiveIntegerField(default=0)
    max_hp = models.PositiveIntegerField(default=30)
    attack = models.PositiveIntegerField(default=5)
    defense = models.PositiveIntegerField(default=1)
    floor = models.PositiveIntegerField(default=1)

    guard_started_at = models.DateTimeField(null=True, blank=True)
    guard_gold_progress_seconds = models.PositiveIntegerField(default=0)
    guard_resource_progress_seconds = models.PositiveIntegerField(default=0)
    guard_resources = models.PositiveIntegerField(default=0)
    guard_total_seconds = models.PositiveBigIntegerField(default=0)
    guard_shifts_completed = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def xp_to_next_level(self):
        return self.level * 20

    @property
    def equipped_attack_bonus(self):
        return sum(x.item.attack_bonus for x in self.inventory.filter(equipped=True).select_related("item"))

    @property
    def equipped_defense_bonus(self):
        return sum(x.item.defense_bonus for x in self.inventory.filter(equipped=True).select_related("item"))

    @property
    def total_attack(self):
        return self.attack + self.equipped_attack_bonus

    @property
    def total_defense(self):
        return self.defense + self.equipped_defense_bonus

    @property
    def guard_active(self):
        return self.guard_started_at is not None

    def guard_elapsed_seconds(self, now=None):
        if not self.guard_started_at:
            return 0
        now = now or timezone.now()
        return max(0, int((now - self.guard_started_at).total_seconds()))

    def guard_pending_rewards(self, now=None):
        elapsed = self.guard_elapsed_seconds(now)
        gold_seconds = self.guard_gold_progress_seconds + elapsed
        resource_seconds = self.guard_resource_progress_seconds + elapsed
        return (
            gold_seconds // GUARD_GOLD_INTERVAL_SECONDS,
            resource_seconds // GUARD_RESOURCE_INTERVAL_SECONDS,
            elapsed,
        )

    def start_guard_duty(self):
        if self.guard_started_at:
            return False
        self.guard_started_at = timezone.now()
        self.save(update_fields=["guard_started_at", "updated_at"])
        return True

    def stop_guard_duty(self):
        if not self.guard_started_at:
            return 0, 0, 0

        now = timezone.now()
        elapsed = self.guard_elapsed_seconds(now)

        gold_seconds = self.guard_gold_progress_seconds + elapsed
        resource_seconds = self.guard_resource_progress_seconds + elapsed
        gold_reward, self.guard_gold_progress_seconds = divmod(gold_seconds, GUARD_GOLD_INTERVAL_SECONDS)
        resource_reward, self.guard_resource_progress_seconds = divmod(resource_seconds, GUARD_RESOURCE_INTERVAL_SECONDS)

        self.gold += gold_reward
        self.guard_resources += resource_reward
        self.guard_total_seconds += elapsed
        self.guard_shifts_completed += 1
        self.guard_started_at = None
        self.save()
        return gold_reward, resource_reward, elapsed

    def grant_xp(self, amount):
        self.xp += amount
        levels = 0
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level += 1
            self.max_hp += 5
            self.attack += 1
            self.defense += 1
            levels += 1
        return levels

    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    character = models.ForeignKey(Character, related_name="inventory", on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    equipped = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["character", "item"], name="unique_character_item")]

    def __str__(self):
        return f"{self.character} - {self.item} x{self.quantity}"
