from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"), path("start/", views.create_character, name="create_character"),
    path("character/", views.character_sheet, name="character"), path("inventory/", views.inventory, name="inventory"),
    path("inventory/<int:entry_id>/equip/", views.toggle_equip, name="toggle_equip"), path("explore/", views.explore, name="explore"),
]
