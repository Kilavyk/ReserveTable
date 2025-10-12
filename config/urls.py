from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("users/", include("users.urls")),
    path("bookings/", include("bookings.urls")),
    path("tables/", include("tables.urls")),
    path("victuals/", include("victuals.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
