# apps/payment_service/serializers.py
from rest_framework import serializers
from .models import PaymentMethod, Payment, Transaction, Refund, VendorPayment


class PaymentMethodSerializer(serializers.ModelSerializer):
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)

    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'user_id', 'payment_type', 'payment_type_display', 'provider',
            'account_number', 'account_holder', 'expiry_date', 'is_default',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'account_number': {'write_only': True},
        }


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_id', 'payment', 'amount', 'transaction_type',
            'status', 'gateway_response', 'created_at'
        ]


class PaymentSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'order_id', 'user_id', 'payment_method', 'amount',
            'currency', 'gateway', 'gateway_payment_id', 'status',
            'error_message', 'created_at', 'updated_at', 'transactions'
        ]


class RefundSerializer(serializers.ModelSerializer):
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Refund
        fields = [
            'id', 'payment', 'amount', 'reason', 'reason_display', 'reason_details',
            'status', 'status_display', 'processed_by', 'created_at', 'updated_at'
        ]


class VendorPaymentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = VendorPayment
        fields = [
            'id', 'vendor_id', 'amount', 'description', 'status',
            'status_display', 'payment_method', 'transaction_details',
            'created_at', 'processed_at'
        ]