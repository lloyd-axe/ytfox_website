from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", include("main.urls")),
    path("admin/", admin.site.urls),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG: #using only media while developing
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)