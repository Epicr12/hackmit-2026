"""Root URL configuration for the AMD monitor."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("home.urls")),
    path("sensors/", include("sensor_info.urls")),
    path("map/", include("mapview.urls")),
    path("risk/", include("risk_eval.urls")),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
