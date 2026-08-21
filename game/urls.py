from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("start/", views.create_character, name="create_character"),
    path("character/", views.character_sheet, name="character"),
    path("inventory/", views.inventory, name="inventory"),
    path("inventory/<int:entry_id>/equip/", views.toggle_equip, name="toggle_equip"),
    path("guard/", views.city_guard, name="city_guard"),
    path("guard/start/", views.guard_start, name="guard_start"),
    path("guard/stop/", views.guard_stop, name="guard_stop"),
    path("explore/", views.explore, name="explore"),
    path("workshop/", views.workshop, name="workshop"),
    path("workshop/craft/<int:recipe_id>/", views.craft_recipe, name="craft_recipe"),
    path("codex/", views.codex, name="codex"),
    path("community/", views.community, name="community"),
    path("auth/discord/", views.discord_login, name="discord_login"),
    path("auth/discord/callback/", views.discord_callback, name="discord_callback"),
    path("auth/logout/", views.discord_logout, name="discord_logout"),
]
