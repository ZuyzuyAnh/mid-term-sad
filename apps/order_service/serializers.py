# apps/order_service/serializers.py
from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem, OrderStatusHistory, Wishlist, WishlistItem


class CartItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id', 'product_id', 'product_name', 'quantity',
            'price_at_time', 'selected_attributes', 'subtotal', 'added_at'
        ]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user_id', 'session_id', 'status', 'created_at', 'updated_at', 'items', 'total', 'items_count']

    def get_total(self, obj):
        return sum(item.quantity * item.price_at_time for item in obj.items.all())

    def get_items_count(self, obj):
        return sum(item.quantity for item in obj.items.all())


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_id', 'product_name', 'product_image_url',
            'quantity', 'price_at_time', 'selected_attributes',
            'vendor_id', 'subtotal'
        ]


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'status', 'notes', 'created_by', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user_id', 'email', 'shipping_address_id',
            'shipping_address_data', 'billing_address_data', 'status',
            'payment_status', 'shipping_method', 'shipping_cost', 'subtotal',
            'tax', 'discount', 'total_amount', 'notes', 'created_at',
            'updated_at', 'items', 'status_history'
        ]


class WishlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishlistItem
        fields = ['id', 'product_id', 'added_at']


class WishlistSerializer(serializers.ModelSerializer):
    items = WishlistItemSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'user_id', 'created_at', 'items']