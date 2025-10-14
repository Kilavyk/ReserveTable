from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

app_name = "bookings"

urlpatterns = [
    path("", views.booking_view, name="booking_view"),
    path("create/", views.create_booking_view, name="create_booking"),
    path("admin-panel/", views.admin_panel_view, name="admin_panel"),
    path("booking/<int:booking_id>/", views.booking_detail_view, name="booking_detail"),
    path(
        "booking/<int:booking_id>/edit/", views.edit_booking_view, name="edit_booking"
    ),
    path(
        "booking/<int:booking_id>/cancel/",
        views.cancel_booking_view,
        name="cancel_booking",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
