# apps/admin_service/models.py
from django.db import models


class AdminSettings(models.Model):
    """Cài đặt quản trị cho hệ thống"""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    updated_by = models.IntegerField(null=True, blank=True)  # Foreign key to Admin User
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key

    class Meta:
        db_table = 'admin_settings'
        verbose_name_plural = 'admin settings'


class SystemConfiguration(models.Model):
    """Cấu hình hệ thống"""
    setting_name = models.CharField(max_length=100, unique=True)
    setting_value = models.TextField()
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)  # Can be accessed by frontend
    data_type = models.CharField(max_length=20)  # e.g., 'string', 'integer', 'boolean', 'json'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.setting_name

    class Meta:
        db_table = 'system_configurations'


class AuditLog(models.Model):
    """Nhật ký hoạt động trong hệ thống"""
    user_id = models.IntegerField(null=True, blank=True)  # Foreign key to User in User Service
    action = models.CharField(max_length=100)
    details = models.JSONField(default=dict)
    ip_address = models.CharField(max_length=50, blank=True)
    service_name = models.CharField(max_length=50)  # Which service triggered this log
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} by User {self.user_id} at {self.timestamp}"

    class Meta:
        db_table = 'audit_logs'
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['action']),
            models.Index(fields=['timestamp']),
        ]


class Banner(models.Model):
    """Banner quảng cáo hiển thị trên trang chủ"""
    POSITION_CHOICES = [
        ('home_top', 'Home Page Top'),
        ('home_middle', 'Home Page Middle'),
        ('home_bottom', 'Home Page Bottom'),
        ('category_page', 'Category Page'),
        ('search_results', 'Search Results Page'),
    ]

    title = models.CharField(max_length=255)
    image = models.CharField(max_length=255)  # URL to image
    link_url = models.CharField(max_length=255, blank=True)
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)  # Higher number = higher priority
    created_by = models.IntegerField()  # Foreign key to Admin User
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'banners'


class NotificationSetting(models.Model):
    """Cài đặt thông báo cho admin"""
    admin_type = models.CharField(max_length=50)  # e.g., 'super_admin', 'content_admin', 'support_admin'
    notification_type = models.CharField(max_length=50)  # e.g., 'new_vendor', 'low_inventory', 'security_alert'
    is_enabled = models.BooleanField(default=True)
    delivery_channels = models.JSONField(default=list)  # e.g., ['email', 'dashboard', 'sms']

    def __str__(self):
        return f"{self.admin_type} - {self.notification_type}"

    class Meta:
        db_table = 'notification_settings'
        unique_together = ('admin_type', 'notification_type')


class AIModel(models.Model):
    """Thông tin về các model AI sử dụng trong hệ thống"""
    MODEL_TYPES = [
        ('recommendation', 'Product Recommendation'),
        ('sentiment', 'Sentiment Analysis'),
        ('fraud', 'Fraud Detection'),
        ('forecasting', 'Sales Forecasting'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('training', 'Training'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
    ]

    name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=50, choices=MODEL_TYPES)
    version = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    accuracy = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    last_trained = models.DateTimeField(null=True, blank=True)
    configuration = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} v{self.version} ({self.get_model_type_display()})"

    class Meta:
        db_table = 'ai_models'
        unique_together = ('name', 'version')