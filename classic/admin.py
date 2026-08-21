from django.contrib import admin

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
    Enchantment,
    EventBoss,
    EventDungeon,
    EventDungeonProgress,
    GearEnhancement,
    Guild,
    GuildMembership,
    Stronghold,
)

for model in [
    BrowserProfile,
    Enchantment,
    GearEnhancement,
    AdventureTemplate,
    ArenaBattle,
    Guild,
    GuildMembership,
    Stronghold,
    CompanionSpecies,
    CharacterCompanion,
    DailyActivity,
    Achievement,
    AchievementUnlock,
    EventBoss,
    BossContribution,
    EventDungeon,
    EventDungeonProgress,
]:
    admin.site.register(model)
