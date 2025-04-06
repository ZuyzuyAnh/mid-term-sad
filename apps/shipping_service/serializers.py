# apps/shipping_service/serializers.py
from rest_framework import serializers
from .models import ShippingMethod, ShippingZone, ZoneRate, Shipment, TrackingInfo, VendorShippingSettings


class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod
        fields = [
            'id', 'name', 'description', 'price', 'estimated_days_min',
            'estimated_days_max', 'is_active'
        ]


class ShippingZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingZone
        fields = ['id', 'name', 'countries']


class ZoneRateSerializer(serializers.ModelSerializer):
    shipping_method_name = serializers.CharField(source='shipping_method.name', read_only=True)

    class Meta:
        model = ZoneRate
        fields = ['id', 'zone', 'shipping_method', 'shipping_method_name', 'price']


class TrackingInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingInfo
        fields = ['id', 'status', 'location', 'description', 'timestamp']


class ShipmentSerializer(serializers.ModelSerializer):
    tracking_info = TrackingInfoSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Shipment
        fields = [
            'id', 'order_id', 'carrier', 'tracking_number', 'shipping_method',
            'status', 'status_display', 'estimated_delivery', 'actual_delivery',
            'shipping_address', 'created_at', 'updated_at', 'tracking_info'
        ]


class VendorShippingSettingsSerializer(serializers.ModelSerializer):
    available_shipping_methods = ShippingMethodSerializer(many=True, read_only=True)

    class Meta:
        model = VendorShippingSettings
        fields = [
            'id', 'vendor_id', 'processing_time_days', 'free_shipping_threshold',
            'shipping_policy', 'return_policy', 'available_shipping_methods'
        ]