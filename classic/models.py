from datetime import timedelta

from django.db import models
from django.utils import timezone

from game.models import Character, InventoryItem, Item


ENERGY_REGEN_SECONDS = 6 * 60
MAX_ENERGY = 100


class BrowserProfile(models.Model):
    character = models.OneToOneField(Character, related_name="classic_profile", on_delete=models.CASCADE)
    adventure_energy = models.PositiveIntegerField(default=MAX_ENERGY)
    energy_updated_at = models.DateTimeField(default=timezone.now)
    honor = models.IntegerField(default=1000)
    arena_wins = models.PositiveIntegerField(default=0)
    arena_losses = models.PositiveIntegerField(default=0)
    arena_win_streak = models.PositiveIntegerField(default=0)
    arena_last_fight_at = models.DateTimeField(null=True, blank=True)
    aura = models.PositiveIntegerField(default=0)
    mount_tier = models.PositiveSmallIntegerField(default=0)
    mount_expires_at = models.DateTimeField(null=True, blank=True)
    login_streak = models.PositiveIntegerField(default=0)
    daily_claim_date = models.DateField(null=True, blank=True)
    fortune_claim_date = models.DateField(null=True, blank=True)

    @property
    def mount_active(self):
        return bool(self.mount_tier and self.mount_expires_at and self.mount_expires_at > timezone.now())

    @property
    def mount_discount(self):
        return {1: 10, 2: 20, 3: 30}.get(self.mount_tier, 0) if self.mount_active else 0

    def refresh_energy(self, now=None):
        now = now or timezone.now()
        elapsed = max(0, int((now - self.energy_updated_at).total_seconds()))
        gained = elapsed // ENERGY_REGEN_SECONDS
        if gained:
            self.adventure_energy = min(MAX_ENERGY, self.adventure_energy + gained)
            self.energy_updated_at += timedelta(seconds=gained * ENERGY_REGEN_SECONDS)
            self.save(update_fields=["adventure_energy", "energy_updated_at"])
        return self.adventure_energy

    def spend_energy(self, base_cost):
        self.refresh_energy()
        actual = max(1, (int(base_cost) * (100 - self.mount_discount) + 99) // 100)
        if self.adventure_energy < actual:
            return False, actual
        self.adventure_energy -= actual
        self.save(update_fields=["adventure_energy"])
        return True, actual


class Enchantment(models.Model):
    name = models.CharField(max_length=80, unique=True)
    description = models.CharField(max_length=240, blank=True)
    attack_bonus = models.PositiveIntegerField(default=0)
    defense_bonus = models.PositiveIntegerField(default=0)
    gold_cost = models.PositiveIntegerField(default=20)

    def __str__(self):
        return self.name


class GearEnhancement(models.Model):
    inventory_item = models.OneToOneField(InventoryItem, related_name="classic_enhancement", on_delete=models.CASCADE)
    upgrade_level = models.PositiveIntegerField(default=0)
    enchantment = models.ForeignKey(Enchantment, null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def attack_bonus(self):
        return self.upgrade_level + (self.enchantment.attack_bonus if self.enchantment else 0)

    @property
    def defense_bonus(self):
        return self.upgrade_level + (self.enchantment.defense_bonus if self.enchantment else 0)


class AdventureTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=300)
    energy_cost = models.PositiveSmallIntegerField(default=10)
    xp_reward = models.PositiveIntegerField(default=10)
    gold_reward = models.PositiveIntegerField(default=5)
    supply_reward = models.PositiveIntegerField(default=0)
    difficulty = models.PositiveSmallIntegerField(default=1)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ArenaBattle(models.Model):
    attacker = models.ForeignKey(Character, related_name="classic_arena_attacks", on_delete=models.CASCADE)
    defender = models.ForeignKey(Character, related_name="classic_arena_defenses", on_delete=models.CASCADE)
    winner = models.ForeignKey(Character, related_name="classic_arena_wins_log", on_delete=models.CASCADE)
    honor_delta = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Guild(models.Model):
    name = models.CharField(max_length=80, unique=True)
    owner = models.ForeignKey(Character, related_name="classic_owned_guilds", on_delete=models.CASCADE)
    treasury_gold = models.PositiveBigIntegerField(default=0)
    instructor_level = models.PositiveSmallIntegerField(default=0)
    treasure_level = models.PositiveSmallIntegerField(default=0)
    raid_level = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class GuildMembership(models.Model):
    ROLE_CHOICES = [("member", "Member"), ("officer", "Officer"), ("leader", "Leader")]
    guild = models.ForeignKey(Guild, related_name="memberships", on_delete=models.CASCADE)
    character = models.OneToOneField(Character, related_name="classic_guild_membership", on_delete=models.CASCADE)
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default="member")
    contributed_gold = models.PositiveBigIntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)


class Stronghold(models.Model):
    character = models.OneToOneField(Character, related_name="classic_stronghold", on_delete=models.CASCADE)
    wood = models.PositiveBigIntegerField(default=0)
    stone = models.PositiveBigIntegerField(default=0)
    souls = models.PositiveBigIntegerField(default=0)
    fortress_level = models.PositiveSmallIntegerField(default=1)
    lumber_level = models.PositiveSmallIntegerField(default=1)
    quarry_level = models.PositiveSmallIntegerField(default=1)
    underworld_level = models.PositiveSmallIntegerField(default=0)
    extractor_level = models.PositiveSmallIntegerField(default=0)
    last_collected_at = models.DateTimeField(default=timezone.now)


class CompanionSpecies(models.Model):
    HABITATS = [("forest", "Forest"), ("cave", "Cave"), ("ruins", "Ruins"), ("city", "City"), ("abyss", "Abyss")]
    name = models.CharField(max_length=80, unique=True)
    habitat = models.CharField(max_length=16, choices=HABITATS, default="forest")
    base_attack = models.PositiveSmallIntegerField(default=1)
    base_defense = models.PositiveSmallIntegerField(default=1)
    supply_cost = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.name


class CharacterCompanion(models.Model):
    character = models.ForeignKey(Character, related_name="classic_companions", on_delete=models.CASCADE)
    species = models.ForeignKey(CompanionSpecies, related_name="owners", on_delete=models.CASCADE)
    level = models.PositiveIntegerField(default=1)
    active = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["character", "species"], name="classic_unique_character_companion")]

    @property
    def attack_bonus(self):
        return self.species.base_attack + max(0, self.level - 1)

    @property
    def defense_bonus(self):
        return self.species.base_defense + max(0, self.level - 1)


class DailyActivity(models.Model):
    character = models.ForeignKey(Character, related_name="classic_daily_activity", on_delete=models.CASCADE)
    date = models.DateField(default=timezone.localdate)
    adventures = models.PositiveSmallIntegerField(default=0)
    arena_wins = models.PositiveSmallIntegerField(default=0)
    dungeon_clears = models.PositiveSmallIntegerField(default=0)
    boss_hits = models.PositiveSmallIntegerField(default=0)
    task_reward_claimed = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["character", "date"], name="classic_unique_character_daily")]


class Achievement(models.Model):
    code = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=240)
    stat_key = models.CharField(max_length=60)
    target = models.PositiveIntegerField(default=1)
    reward_gold = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.name


class AchievementUnlock(models.Model):
    character = models.ForeignKey(Character, related_name="classic_achievement_unlocks", on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, related_name="unlocks", on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["character", "achievement"], name="classic_unique_character_achievement")]


class EventBoss(models.Model):
    name = models.CharField(max_length=100)
    max_hp = models.PositiveBigIntegerField(default=10000)
    current_hp = models.PositiveBigIntegerField(default=10000)
    starts_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    @property
    def is_open(self):
        now = timezone.now()
        return self.active and self.current_hp > 0 and self.starts_at <= now and (self.ends_at is None or self.ends_at > now)

    def __str__(self):
        return self.name


class BossContribution(models.Model):
    boss = models.ForeignKey(EventBoss, related_name="contributions", on_delete=models.CASCADE)
    character = models.ForeignKey(Character, related_name="classic_boss_contributions", on_delete=models.CASCADE)
    damage = models.PositiveBigIntegerField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["boss", "character"], name="classic_unique_boss_character")]


class EventDungeon(models.Model):
    name = models.CharField(max_length=100)
    max_floor = models.PositiveIntegerField(default=50)
    starts_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    @property
    def is_open(self):
        now = timezone.now()
        return self.active and self.starts_at <= now and (self.ends_at is None or self.ends_at > now)

    def __str__(self):
        return self.name


class EventDungeonProgress(models.Model):
    dungeon = models.ForeignKey(EventDungeon, related_name="progress_entries", on_delete=models.CASCADE)
    character = models.ForeignKey(Character, related_name="classic_event_progress", on_delete=models.CASCADE)
    floor = models.PositiveIntegerField(default=1)
    clears = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["dungeon", "character"], name="classic_unique_event_character")]


class Colony(models.Model):
    character = models.OneToOneField(Character, related_name="colony", on_delete=models.CASCADE)
    inhabitants = models.PositiveIntegerField(default=3)
    lifetime_recruited = models.PositiveBigIntegerField(default=3)
    treasury_level = models.PositiveSmallIntegerField(default=0)
    market_level = models.PositiveSmallIntegerField(default=0)
    hunters_level = models.PositiveSmallIntegerField(default=0)
    training_level = models.PositiveSmallIntegerField(default=0)
    workshop_level = models.PositiveSmallIntegerField(default=0)
    last_gold_collected_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.character.name} Colony"
