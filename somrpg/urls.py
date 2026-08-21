from django.contrib import admin
from django.urls import include, path

handler404 = "game.error_views.page_not_found"
handler500 = "game.error_views.server_error"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("town/", include("classic.urls")),
    path("", include("game.urls")),
]
