from django.contrib import admin

from .models import (
    Character,
    CodexDiscovery,
    CommunitySeason,
    CraftingRecipe,
    DiscordProfile,
    Enemy,
    FloorBoss,
    FloorShopOffer,
    InventoryItem,
    Item,
    SeasonProgress,
    TowerFloor,
)


class InventoryInline(admin.TabularInline):
    model = InventoryItem
    extra = 0


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "archetype",
        "level",
        "floor",
        "dungeon_clears",
        "total_gold_earned",
        "crafting_xp",
        "guard_resources",
        "updated_at",
    )
    list_filter = ("archetype",)
    inlines = [InventoryInline]


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "rarity", "slot", "unlock_floor", "shop_price", "shop_enabled", "attack_bonus", "defense_bonus")
    list_filter = ("rarity", "slot", "shop_enabled", "unlock_floor")


@admin.register(Enemy)
class EnemyAdmin(admin.ModelAdmin):
    list_display = ("name", "floor_min", "floor_max", "is_boss", "max_hp", "attack", "defense", "xp_reward", "enabled")
    list_filter = ("is_boss", "enabled")


@admin.register(TowerFloor)
class TowerFloorAdmin(admin.ModelAdmin):
    list_display = ("floor_number", "name", "biome", "shop_name", "safe_zone")
    ordering = ("floor_number",)


@admin.register(FloorBoss)
class FloorBossAdmin(admin.ModelAdmin):
    list_display = ("floor", "enemy", "title")


@admin.register(FloorShopOffer)
class FloorShopOfferAdmin(admin.ModelAdmin):
    list_display = ("unlock_floor", "item", "price", "enabled")
    list_filter = ("unlock_floor", "enabled")


@admin.register(CommunitySeason)
class CommunitySeasonAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "starts_at", "ends_at", "active")
    list_filter = ("active",)


@admin.register(SeasonProgress)
class SeasonProgressAdmin(admin.ModelAdmin):
    list_display = ("season", "character", "dungeon_clears", "commerce_gold", "crafting_xp", "updated_at")
    list_filter = ("season",)


@admin.register(CraftingRecipe)
class CraftingRecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "output_item", "supply_cost", "gold_cost", "xp_reward", "enabled")
    list_filter = ("enabled",)


@admin.register(DiscordProfile)
class DiscordProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "discord_id", "user", "updated_at")


@admin.register(CodexDiscovery)
class CodexDiscoveryAdmin(admin.ModelAdmin):
    list_display = ("character", "entry_type", "label", "discovered_at")
    list_filter = ("entry_type",)


admin.site.register(InventoryItem)
