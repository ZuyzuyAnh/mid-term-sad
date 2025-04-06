from django.urls import path
from . import views

app_name = 'payment_service'

urlpatterns = [
    # Payment Methods
    path('methods/', views.payment_methods, name='payment_methods'),
    path('methods/add/', views.add_payment_method, name='add_payment_method'),
    path('methods/<int:pk>/update/', views.update_payment_method, name='update_payment_method'),
    path('methods/<int:pk>/delete/', views.delete_payment_method, name='delete_payment_method'),
    path('methods/<int:pk>/set-default/', views.set_default_payment_method, name='set_default_payment_method'),

    # Payment Processing
    path('process/<int:order_id>/', views.process_payment, name='process_payment'),
    path('callback/<str:gateway>/', views.payment_callback, name='payment_callback'),
    path('success/', views.payment_success, name='payment_success'),
    path('failed/', views.payment_failed, name='payment_failed'),

    # Refunds
    path('refunds/request/<int:order_id>/', views.request_refund, name='request_refund'),
    path('refunds/', views.refund_list, name='refund_list'),
    path('refunds/<int:pk>/', views.refund_detail, name='refund_detail'),

    # Vendor Payment Management
    path('vendor/transactions/', views.vendor_transactions, name='vendor_transactions'),
    path('vendor/earnings/', views.vendor_earnings, name='vendor_earnings'),
    path('vendor/withdraw/', views.vendor_withdraw, name='vendor_withdraw'),

    # Payment API
    path('api/available-gateways/', views.available_payment_gateways, name='available_payment_gateways'),
    path('api/transaction-status/<str:transaction_id>/', views.transaction_status, name='transaction_status'),
]