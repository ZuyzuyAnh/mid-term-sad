# apps/product_service/serializers.py
from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductAttribute, ProductAttributeValue, Inventory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'image', 'status', 'created_at']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_primary', 'alt_text']


class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = ['id', 'name', 'description']


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)

    class Meta:
        model = ProductAttributeValue
        fields = ['id', 'attribute', 'attribute_name', 'value']


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ['id', 'quantity', 'last_updated', 'threshold_quantity', 'is_low_stock']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    attributes = ProductAttributeValueSerializer(source='attribute_values', many=True, read_only=True)
    inventory_status = serializers.SerializerMethodField()
    discount_percentage = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description', 'seller_id',
            'category', 'category_name', 'price', 'discount_price', 'quantity',
            'status', 'featured', 'created_at', 'updated_at', 'images',
            'attributes', 'inventory_status', 'discount_percentage'
        ]

    def get_inventory_status(self, obj):
        try:
            inventory = obj.inventory
            return {
                'quantity': inventory.quantity,
                'is_low_stock': inventory.is_low_stock,
                'threshold': inventory.threshold_quantity
            }
        except Inventory.DoesNotExist:
            return None