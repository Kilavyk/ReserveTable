from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'victuals'

urlpatterns = [
    path('menu/', views.menu_view, name='menu'),
    path('management/', views.menu_management, name='menu_management'),
    path('add/', views.add_menu_item, name='add_menu_item'),
    path('edit/', views.edit_menu_item, name='edit_menu_item'),
    path('delete/', views.delete_menu_item, name='delete_menu_item'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
