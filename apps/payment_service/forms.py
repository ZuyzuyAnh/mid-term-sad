# apps/payment_service/forms.py
from django import forms
from .models import PaymentMethod, Refund


class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['payment_type', 'provider', 'account_number', 'account_holder', 'expiry_date', 'is_default']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'account_number': forms.TextInput(attrs={'autocomplete': 'off'}),
        }


class RefundRequestForm(forms.ModelForm):
    class Meta:
        model = Refund
        fields = ['amount', 'reason', 'reason_details']
        widgets = {
            'reason_details': forms.Textarea(attrs={'rows': 3}),
        }


class PaymentProcessForm(forms.Form):
    PAYMENT_GATEWAY_CHOICES = [
        ('direct', 'Thanh toán trực tiếp'),
        ('vnpay', 'VNPay'),
        ('momo', 'MoMo'),
        ('zalopay', 'ZaloPay'),
    ]

    payment_method_id = forms.CharField(required=False, widget=forms.HiddenInput())
    payment_gateway = forms.ChoiceField(
        choices=PAYMENT_GATEWAY_CHOICES,
        required=True,
        label="Cổng thanh toán"
    )
    agree_terms = forms.BooleanField(
        required=True,
        label="Tôi đồng ý với điều khoản thanh toán"
    )


class VendorWithdrawForm(forms.Form):
    PAYMENT_METHOD_CHOICES = [
        ('bank_transfer', 'Chuyển khoản ngân hàng'),
        ('e_wallet', 'Ví điện tử'),
    ]

    amount = forms.DecimalField(
        min_value=50000,
        required=True,
        label="Số tiền rút (VNĐ)",
        help_text="Số tiền tối thiểu: 50,000 VNĐ"
    )
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        required=True,
        label="Phương thức thanh toán"
    )
    bank_name = forms.CharField(required=False, label="Tên ngân hàng")
    account_number = forms.CharField(required=False, label="Số tài khoản")
    account_holder = forms.CharField(required=False, label="Tên chủ tài khoản")
    e_wallet_number = forms.CharField(required=False, label="Số ví điện tử")