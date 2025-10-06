from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('menu/', views.menu, name='menu'),
    path('contacts/', views.contacts, name='contacts'),
    path('feedback/', views.feedback, name='feedback'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
