from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'tables'

urlpatterns = [
    path('management/', views.tables_management_view, name='management'),
    path('add/', views.add_table_view, name='add_table'),
    path('edit/', views.edit_table_view, name='edit_table'),
    path('delete/', views.delete_table_view, name='delete_table'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
