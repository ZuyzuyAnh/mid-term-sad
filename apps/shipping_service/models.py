# apps/shipping_service/models.py
from django.db import models


class ShippingMethod(models.Model):
    """Phương thức vận chuyển"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_days_min = models.PositiveIntegerField()
    estimated_days_max = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'shipping_methods'


class ShippingZone(models.Model):
    """Khu vực vận chuyển"""
    name = models.CharField(max_length=100)
    countries = models.JSONField()  # List of country codes

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'shipping_zones'


class ZoneRate(models.Model):
    """Giá vận chuyển theo khu vực"""
    zone = models.ForeignKey(ShippingZone, on_delete=models.CASCADE, related_name='rates')
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.zone.name} - {self.shipping_method.name}: {self.price}"

    class Meta:
        db_table = 'zone_rates'
        unique_together = ('zone', 'shipping_method')


class Shipment(models.Model):
    """Đơn vận chuyển"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed Delivery Attempt'),
        ('returned', 'Returned to Sender'),
    ]

    order_id = models.IntegerField()  # Foreign key to Order in Order Service
    carrier = models.CharField(max_length=100)
    tracking_number = models.CharField(max_length=100, blank=True)
    shipping_method = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    estimated_delivery = models.DateField(null=True, blank=True)
    actual_delivery = models.DateTimeField(null=True, blank=True)
    shipping_address = models.JSONField()  # Stored copy of address at time of shipment
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Shipment {self.id} for Order {self.order_id} - {self.status}"

    class Meta:
        db_table = 'shipments'


class TrackingInfo(models.Model):
    """Thông tin theo dõi vận chuyển"""
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='tracking_info')
    status = models.CharField(max_length=50)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.shipment.tracking_number} - {self.status} at {self.timestamp}"

    class Meta:
        db_table = 'tracking_info'
        ordering = ['-timestamp']


class VendorShippingSettings(models.Model):
    """Cài đặt vận chuyển của người bán"""
    vendor_id = models.IntegerField(unique=True)  # Foreign key to Vendor User in User Service
    processing_time_days = models.PositiveIntegerField(default=1)
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    shipping_policy = models.TextField(blank=True)
    return_policy = models.TextField(blank=True)
    available_shipping_methods = models.ManyToManyField(ShippingMethod)

    def __str__(self):
        return f"Shipping settings for Vendor {self.vendor_id}"

    class Meta:
        db_table = 'vendor_shipping_settings'