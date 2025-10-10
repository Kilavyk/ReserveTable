from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'victuals'

urlpatterns = [
    path('menu/', views.menu_view, name='menu'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
