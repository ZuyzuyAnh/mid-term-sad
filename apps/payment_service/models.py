# apps/payment_service/models.py
from django.db import models
import uuid


class PaymentMethod(models.Model):
    """Phương thức thanh toán của người dùng"""
    METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('paypal', 'PayPal'),
        ('momo', 'MoMo'),
        ('zalopay', 'ZaloPay'),
        ('cod', 'Cash On Delivery'),
    ]

    user_id = models.IntegerField()  # Foreign key to User in other DB
    payment_type = models.CharField(max_length=20, choices=METHOD_CHOICES)
    provider = models.CharField(max_length=50, blank=True)  # e.g., Visa, Mastercard
    account_number = models.CharField(max_length=255, blank=True)  # Encrypted account number
    account_holder = models.CharField(max_length=255, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_id} - {self.get_payment_type_display()}"

    def save(self, *args, **kwargs):
        # Ensure only one default payment method per user
        if self.is_default:
            PaymentMethod.objects.filter(user_id=self.user_id, is_default=True).exclude(id=self.id).update(
                is_default=False)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'payment_methods'


class Payment(models.Model):
    """Thanh toán"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]

    order_id = models.IntegerField()  # Foreign key to Order in Order Service
    user_id = models.IntegerField(null=True, blank=True)  # Foreign key to User in User Service
    payment_method = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='VND')
    gateway = models.CharField(max_length=50)  # Payment gateway used
    gateway_payment_id = models.CharField(max_length=255, blank=True)  # Payment ID from gateway
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} for Order {self.order_id} - {self.status}"

    class Meta:
        db_table = 'payments'


class Transaction(models.Model):
    """Giao dịch thanh toán"""
    TRANSACTION_TYPES = [
        ('charge', 'Charge'),
        ('refund', 'Refund'),
        ('transfer', 'Transfer'),
    ]

    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=20)
    gateway_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.transaction_type} - {self.amount}"

    class Meta:
        db_table = 'transactions'


class Refund(models.Model):
    """Hoàn tiền"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('declined', 'Declined'),
    ]

    REASON_CHOICES = [
        ('defective', 'Defective Product'),
        ('not_as_described', 'Not As Described'),
        ('wrong_item', 'Wrong Item Received'),
        ('late_delivery', 'Late Delivery'),
        ('damaged', 'Damaged in Transit'),
        ('changed_mind', 'Changed Mind'),
        ('other', 'Other'),
    ]

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    reason_details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processed_by = models.IntegerField(null=True, blank=True)  # Foreign key to Admin/Support User
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Refund {self.id} for Payment {self.payment.id} - {self.status}"

    class Meta:
        db_table = 'refunds'


class VendorPayment(models.Model):
    """Thanh toán cho người bán"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    vendor_id = models.IntegerField()  # Foreign key to Vendor User in User Service
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50)
    transaction_details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Vendor Payment {self.id} to Vendor {self.vendor_id} - {self.status}"

    class Meta:
        db_table = 'vendor_payments'