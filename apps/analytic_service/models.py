# apps/analytic_service/models.py
from django.db import models
from djongo.models import DjongoManager


class UserActivity(models.Model):
    """Hoạt động của người dùng trên hệ thống"""
    user_id = models.IntegerField(null=True, blank=True)  # Foreign key to User in User Service
    session_id = models.CharField(max_length=255, blank=True)  # For tracking non-logged users
    ip_address = models.CharField(max_length=50, blank=True)
    activity_type = models.CharField(max_length=50)  # e.g., 'page_view', 'product_view', 'add_to_cart'
    page = models.CharField(max_length=255, blank=True)
    product_id = models.IntegerField(null=True, blank=True)
    category_id = models.IntegerField(null=True, blank=True)
    device_info = models.JSONField(default=dict, blank=True)
    referrer = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = DjongoManager()

    def __str__(self):
        return f"{self.activity_type} by {'User ' + str(self.user_id) if self.user_id else 'Guest'} at {self.timestamp}"

    class Meta:
        db_table = 'user_activities'
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['activity_type']),
            models.Index(fields=['timestamp']),
        ]


class SellerAnalytics(models.Model):
    """Phân tích dữ liệu người bán"""
    seller_id = models.IntegerField()  # Foreign key to Vendor in User Service
    period = models.CharField(max_length=20)  # e.g., 'daily', 'weekly', 'monthly', 'yearly'
    period_start = models.DateField()
    period_end = models.DateField()
    total_sales = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    average_order_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    product_performance = models.JSONField(default=dict)  # Top/bottom performing products
    average_rating = models.FloatField(default=0)
    generated_at = models.DateTimeField(auto_now_add=True)

    objects = DjongoManager()

    def __str__(self):
        return f"Analytics for Seller {self.seller_id} - {self.period} ({self.period_start} to {self.period_end})"

    class Meta:
        db_table = 'seller_analytics'
        unique_together = ('seller_id', 'period', 'period_start')
        indexes = [
            models.Index(fields=['seller_id']),
            models.Index(fields=['period_start']),
        ]


class ProductPerformance(models.Model):
    """Hiệu suất của sản phẩm"""
    product_id = models.IntegerField()  # Foreign key to Product in Product Service
    period = models.CharField(max_length=20)  # e.g., 'daily', 'weekly', 'monthly', 'yearly'
    period_start = models.DateField()
    period_end = models.DateField()
    views = models.IntegerField(default=0)
    unique_views = models.IntegerField(default=0)
    cart_adds = models.IntegerField(default=0)
    purchases = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    conversion_rate = models.FloatField(default=0)
    average_rating = models.FloatField(default=0)
    generated_at = models.DateTimeField(auto_now_add=True)

    objects = DjongoManager()

    def __str__(self):
        return f"Performance for Product {self.product_id} - {self.period} ({self.period_start} to {self.period_end})"

    class Meta:
        db_table = 'product_performance'
        unique_together = ('product_id', 'period', 'period_start')
        indexes = [
            models.Index(fields=['product_id']),
            models.Index(fields=['period_start']),
        ]


class SearchQuery(models.Model):
    """Lưu trữ các truy vấn tìm kiếm của người dùng"""
    query_text = models.CharField(max_length=255)
    user_id = models.IntegerField(null=True, blank=True)  # Foreign key to User in User Service
    session_id = models.CharField(max_length=255, blank=True)
    results_count = models.IntegerField()
    filters_applied = models.JSONField(default=dict, blank=True)
    clicked_products = models.JSONField(default=list, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = DjongoManager()

    def __str__(self):
        return f"Search: '{self.query_text}' ({self.results_count} results)"

    class Meta:
        db_table = 'search_queries'
        indexes = [
            models.Index(fields=['query_text']),
            models.Index(fields=['timestamp']),
        ]


class AggregatedStatistics(models.Model):
    """Thống kê tổng hợp của hệ thống"""
    metric_name = models.CharField(max_length=100)  # e.g., 'total_sales', 'active_users', 'conversion_rate'
    period = models.CharField(max_length=20)  # e.g., 'daily', 'weekly', 'monthly', 'yearly'
    period_start = models.DateField()
    period_end = models.DateField()
    value = models.FloatField()
    additional_data = models.JSONField(default=dict, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    objects = DjongoManager()

    def __str__(self):
        return f"{self.metric_name} - {self.period} ({self.period_start} to {self.period_end}): {self.value}"

    class Meta:
        db_table = 'aggregated_statistics'
        unique_together = ('metric_name', 'period', 'period_start')
        indexes = [
            models.Index(fields=['metric_name']),
            models.Index(fields=['period_start']),
        ]