from django.urls import path

from . import views

app_name = "classic"

urlpatterns = [
    path("", views.town, name="town"),
    path("action/", views.action, name="action"),
]
