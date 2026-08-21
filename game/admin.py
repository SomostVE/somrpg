from django.contrib import admin
from .models import Character, Enemy, InventoryItem, Item


class InventoryInline(admin.TabularInline):
    model = InventoryItem
    extra = 0


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ("name", "level", "xp", "gold", "floor", "updated_at")
    inlines = [InventoryInline]


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "rarity", "attack_bonus", "defense_bonus")


@admin.register(Enemy)
class EnemyAdmin(admin.ModelAdmin):
    list_display = ("name", "floor_min", "max_hp", "attack", "defense", "xp_reward", "enabled")

admin.site.register(InventoryItem)
