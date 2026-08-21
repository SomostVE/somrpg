from django.urls import path

from . import api_views, index_views, views


urlpatterns = [
    path("", views.home, name="home"),
    path("start/", views.create_character, name="create_character"),
    path("character/", views.character_sheet, name="character"),
    path("tower/", views.tower_map, name="tower_map"),
    path("tower/<int:floor_number>/travel/", views.travel_floor, name="travel_floor"),
    path("shop/", views.floor_shop, name="floor_shop"),
    path("shop/<int:offer_id>/buy/", views.buy_floor_shop_item, name="buy_floor_shop_item"),
    path("inventory/", views.inventory, name="inventory"),
    path("inventory/<int:entry_id>/equip/", views.toggle_equip, name="toggle_equip"),
    path("guard/", views.city_guard, name="city_guard"),
    path("guard/start/", views.guard_start, name="guard_start"),
    path("guard/stop/", views.guard_stop, name="guard_stop"),
    path("explore/", views.explore, name="explore"),
    path("workshop/", views.workshop, name="workshop"),
    path("workshop/craft/<int:recipe_id>/", views.craft_recipe, name="craft_recipe"),
    path("codex/", views.codex, name="codex"),
    path("index/", index_views.content_index, name="content_index"),
    path("community/", views.community, name="community"),
    path("api/version/", api_views.version_status, name="version_status"),
    path("api/chat/", api_views.live_chat, name="live_chat"),
    path("auth/discord/", views.discord_login, name="discord_login"),
    path("auth/discord/callback/", views.discord_callback, name="discord_callback"),
    path("auth/logout/", views.discord_logout, name="discord_logout"),
]
