# apps/order_service/models.py
from django.db import models
from django.utils import timezone


class Cart(models.Model):
    """Giỏ hàng của người dùng"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('merged', 'Merged'),
        ('converted', 'Converted to Order'),
        ('abandoned', 'Abandoned'),
    ]

    user_id = models.IntegerField(null=True, blank=True)  # Foreign key to User in other DB
    session_id = models.CharField(max_length=255, null=True, blank=True)  # For non-logged in users
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.id} - {'User ' + str(self.user_id) if self.user_id else 'Guest'}"

    class Meta:
        db_table = 'carts'


class CartItem(models.Model):
    """Item trong giỏ hàng"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField()  # Foreign key to Product in other DB
    product_name = models.CharField(max_length=255)  # Cache product name
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)  # Price when added to cart
    selected_attributes = models.JSONField(default=dict, blank=True)  # Store selected attributes as JSON
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_name} ({self.quantity}) in Cart {self.cart.id}"

    @property
    def subtotal(self):
        return self.quantity * self.price_at_time

    class Meta:
        db_table = 'cart_items'


class Order(models.Model):
    """Đơn hàng"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]

    user_id = models.IntegerField(null=True, blank=True)  # Foreign key to User in other DB
    order_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField()  # Customer email for guest checkout
    shipping_address_id = models.IntegerField(null=True, blank=True)  # Foreign key to Address in User Service
    shipping_address_data = models.JSONField()  # Stored copy of address at time of order
    billing_address_data = models.JSONField(null=True, blank=True)  # Stored copy of billing address
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    shipping_method = models.CharField(max_length=100)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.order_number}"

    def save(self, *args, **kwargs):
        # Generate order number if not already set
        if not self.order_number:
            last_order = Order.objects.order_by('-id').first()
            last_id = last_order.id if last_order else 0
            self.order_number = f"ORD{timezone.now().strftime('%Y%m%d')}{last_id + 1:04d}"
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'orders'


class OrderItem(models.Model):
    """Item trong đơn hàng"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField()  # Foreign key to Product in other DB
    product_name = models.CharField(max_length=255)  # Cached product name
    product_image_url = models.CharField(max_length=255, blank=True)  # Cached product image
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)  # Price when ordered
    selected_attributes = models.JSONField(default=dict, blank=True)  # Store selected attributes as JSON
    vendor_id = models.IntegerField()  # Foreign key to Vendor in User Service
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} ({self.quantity}) in Order #{self.order.order_number}"

    class Meta:
        db_table = 'order_items'


class OrderStatusHistory(models.Model):
    """Lịch sử trạng thái đơn hàng"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    notes = models.TextField(blank=True)
    created_by = models.IntegerField(null=True, blank=True)  # Foreign key to User in User Service
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.order.order_number} - {self.status}"

    class Meta:
        db_table = 'order_status_history'


class Wishlist(models.Model):
    """Danh sách yêu thích"""
    user_id = models.IntegerField()  # Foreign key to User in other DB
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist for User {self.user_id}"

    class Meta:
        db_table = 'wishlists'


class WishlistItem(models.Model):
    """Item trong danh sách yêu thích"""
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField()  # Foreign key to Product in other DB
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Product {self.product_id} in Wishlist for User {self.wishlist.user_id}"

    class Meta:
        db_table = 'wishlist_items'
        unique_together = ('wishlist', 'product_id')