from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'users'

urlpatterns = [
    path('login/', views.custom_login_view, name='login'),
    path('register/', views.custom_register_view, name='register'),
    path('logout/', views.custom_logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('verify/<str:token>/', views.email_verification, name='email_verification'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset-confirm/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),

    path('management/', views.users_management_view, name='users_management'),
    path('add/', views.add_user_view, name='add_user'),
    path('edit/', views.edit_user_view, name='edit_user'),
    path('delete/', views.delete_user_view, name='delete_user'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
