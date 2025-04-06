# apps/admin_service/serializers.py
from rest_framework import serializers
from .models import (
    AdminSettings, SystemConfiguration, AuditLog,
    Banner, NotificationSetting, AIModel
)


class AdminSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminSettings
        fields = ['id', 'key', 'value', 'description', 'updated_by', 'updated_at']


class SystemConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfiguration
        fields = [
            'id', 'setting_name', 'setting_value', 'description',
            'is_public', 'data_type', 'created_at', 'updated_at'
        ]


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user_id', 'action', 'details', 'ip_address',
            'service_name', 'timestamp'
        ]


class BannerSerializer(serializers.ModelSerializer):
    position_display = serializers.CharField(source='get_position_display', read_only=True)

    class Meta:
        model = Banner
        fields = [
            'id', 'title', 'image', 'link_url', 'position', 'position_display',
            'start_date', 'end_date', 'is_active', 'priority', 'created_by',
            'created_at', 'updated_at'
        ]


class NotificationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSetting
        fields = [
            'id', 'admin_type', 'notification_type', 'is_enabled', 'delivery_channels'
        ]


class AIModelSerializer(serializers.ModelSerializer):
    model_type_display = serializers.CharField(source='get_model_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = AIModel
        fields = [
            'id', 'name', 'model_type', 'model_type_display', 'version', 'description',
            'accuracy', 'status', 'status_display', 'last_trained', 'configuration',
            'created_at', 'updated_at'
        ]