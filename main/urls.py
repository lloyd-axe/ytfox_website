from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path("", views.index, name="index"),
    path('yt_get/', views.index, name="yt_get"),
    path('yt_dl/', views.yt_dl, name="yt_dl")
]