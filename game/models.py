from django.db import models


class Item(models.Model):
    RARITY_CHOICES = [("common", "Common"), ("uncommon", "Uncommon"), ("rare", "Rare"), ("epic", "Epic"), ("legendary", "Legendary")]
    name = models.CharField(max_length=80, unique=True)
    description = models.CharField(max_length=240, blank=True)
    rarity = models.CharField(max_length=16, choices=RARITY_CHOICES, default="common")
    attack_bonus = models.PositiveIntegerField(default=0)
    defense_bonus = models.PositiveIntegerField(default=0)

    def __str__(self): return self.name


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

    class Meta: ordering = ["floor_min", "name"]
    def __str__(self): return self.name


class Character(models.Model):
    name = models.CharField(max_length=40, default="Adventurer")
    level = models.PositiveIntegerField(default=1)
    xp = models.PositiveIntegerField(default=0)
    gold = models.PositiveIntegerField(default=0)
    max_hp = models.PositiveIntegerField(default=30)
    attack = models.PositiveIntegerField(default=5)
    defense = models.PositiveIntegerField(default=1)
    floor = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def xp_to_next_level(self): return self.level * 20
    @property
    def equipped_attack_bonus(self): return sum(x.item.attack_bonus for x in self.inventory.filter(equipped=True).select_related("item"))
    @property
    def equipped_defense_bonus(self): return sum(x.item.defense_bonus for x in self.inventory.filter(equipped=True).select_related("item"))
    @property
    def total_attack(self): return self.attack + self.equipped_attack_bonus
    @property
    def total_defense(self): return self.defense + self.equipped_defense_bonus

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

    def __str__(self): return self.name


class InventoryItem(models.Model):
    character = models.ForeignKey(Character, related_name="inventory", on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    equipped = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["character", "item"], name="unique_character_item")]

    def __str__(self): return f"{self.character} - {self.item} x{self.quantity}"
