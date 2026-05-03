from django.urls import path

from . import views

urlpatterns = [
    path("", views.monitor, name="monitor"),
    path("connect/", views.fs_connect, name="fs_connect"),
]
