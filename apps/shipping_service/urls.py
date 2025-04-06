from django.urls import path
from . import views

app_name = 'shipping_service'

urlpatterns = [
    # Shipping Methods
    path('methods/', views.shipping_methods, name='shipping_methods'),
    path('calculate/', views.calculate_shipping, name='calculate_shipping'),

    # Shipment Tracking
    path('tracking/<str:tracking_number>/', views.track_shipment, name='track_shipment'),
    path('shipments/<int:order_id>/', views.shipment_details, name='shipment_details'),

    # Address Validation
    path('validate-address/', views.validate_address, name='validate_address'),

    # Vendor Shipping Management
    path('vendor/shipments/', views.vendor_shipments, name='vendor_shipments'),
    path('vendor/shipments/<int:pk>/update/', views.update_shipment, name='update_shipment'),
    path('vendor/shipping-settings/', views.vendor_shipping_settings, name='vendor_shipping_settings'),

    # Shipping Zones
    path('zones/', views.shipping_zones, name='shipping_zones'),
    path('zones/<int:pk>/', views.shipping_zone_detail, name='shipping_zone_detail'),

    # Shipping API
    path('api/shipping-options/<int:order_id>/', views.get_shipping_options, name='get_shipping_options'),
    path('api/generate-label/<int:shipment_id>/', views.generate_shipping_label, name='generate_shipping_label'),
]