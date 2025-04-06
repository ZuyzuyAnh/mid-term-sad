# apps/user_service/serializers.py
from rest_framework import serializers
from .models import User, UserProfile, Address, UserPermission

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'phone_number', 'birth_date', 'profile_picture', 'loyalty_points', 'is_vendor', 'vendor_approved']
        read_only_fields = ['loyalty_points', 'vendor_approved']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'street_address', 'city', 'state', 'zip_code', 'country', 'address_type', 'is_default', 'phone_number']

class UserPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPermission
        fields = ['id', 'permission_name', 'is_allowed']