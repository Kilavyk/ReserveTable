from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'bookings'

urlpatterns = [
    path('', views.booking_view, name='booking_view'),
    path('create/', views.create_booking_view, name='create_booking'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)