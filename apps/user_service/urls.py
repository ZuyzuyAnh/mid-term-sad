from django.urls import path
from . import views

app_name = 'user_service'

urlpatterns = [
    # Authentication
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('password-reset/', views.password_reset, name='password_reset'),
    path('password-reset/confirm/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),

    # Profile Management
    path('profile/', views.user_profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),

    # Address Management
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/add/', views.add_address, name='add_address'),
    path('addresses/<int:pk>/update/', views.update_address, name='update_address'),
    path('addresses/<int:pk>/delete/', views.delete_address, name='delete_address'),
    path('addresses/<int:pk>/set-default/', views.set_default_address, name='set_default_address'),

    # Vendor Management
    path('vendor-register/', views.vendor_register, name='vendor_register'),
    path('vendor-profile/', views.vendor_profile, name='vendor_profile'),
    path('vendor-profile/update/', views.update_vendor_profile, name='update_vendor_profile'),

    # User API
    path('api/current-user/', views.current_user_api, name='current_user_api'),
    path('api/check-email/', views.check_email_exists, name='check_email_exists'),
    path('api/check-username/', views.check_username_exists, name='check_username_exists'),
]