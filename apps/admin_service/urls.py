from django.urls import path
from . import views

app_name = 'admin_service'

urlpatterns = [
    # User Management
    path('users/', views.user_management, name='user_management'),
    path('users/<int:pk>/', views.user_details, name='user_details'),
    path('users/<int:pk>/update/', views.update_user, name='update_user'),
    path('users/<int:pk>/delete/', views.delete_user, name='delete_user'),

    # Vendor Management
    path('vendors/', views.vendor_management, name='vendor_management'),
    path('vendors/pending/', views.pending_vendors, name='pending_vendors'),
    path('vendors/<int:pk>/approve/', views.approve_vendor, name='approve_vendor'),
    path('vendors/<int:pk>/decline/', views.decline_vendor, name='decline_vendor'),

    # Content Management
    path('content/', views.content_management, name='content_management'),
    path('content/banners/', views.manage_banners, name='manage_banners'),
    path('content/banners/add/', views.add_banner, name='add_banner'),
    path('content/banners/<int:pk>/update/', views.update_banner, name='update_banner'),
    path('content/banners/<int:pk>/delete/', views.delete_banner, name='delete_banner'),

    # System Configuration
    path('config/', views.system_configuration, name='system_configuration'),
    path('config/general/', views.general_settings, name='general_settings'),
    path('config/email/', views.email_settings, name='email_settings'),
    path('config/payment/', views.payment_settings, name='payment_settings'),
    path('config/shipping/', views.shipping_settings, name='shipping_settings'),

    # Security Management
    path('security/', views.security_management, name='security_management'),
    path('security/logs/', views.audit_logs, name='audit_logs'),
    path('security/permissions/', views.manage_permissions, name='manage_permissions'),

    # AI Management
    path('ai/models/', views.ai_models, name='ai_models'),
    path('ai/models/<int:pk>/update/', views.update_ai_model, name='update_ai_model'),
    path('ai/train/<str:model_type>/', views.train_ai_model, name='train_ai_model'),

    # Admin API
    path('api/system-health/', views.system_health, name='system_health'),
    path('api/backup/', views.create_backup, name='create_backup'),
]