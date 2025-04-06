# apps/order_service/forms.py
from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class ShippingForm(forms.Form):
    shipping_method = forms.ChoiceField(
        choices=[],  # Sẽ được cập nhật động
        required=True,
        label="Phương thức vận chuyển"
    )

    def __init__(self, *args, **kwargs):
        shipping_methods = kwargs.pop('shipping_methods', [])
        super(ShippingForm, self).__init__(*args, **kwargs)

        # Cập nhật danh sách phương thức vận chuyển
        self.fields['shipping_method'].choices = [
            (method['id'],
             f"{method['name']} ({method['price']}đ - {method['estimated_days_min']}-{method['estimated_days_max']} ngày)")
            for method in shipping_methods
        ]


class PaymentForm(forms.Form):
    payment_method = forms.ChoiceField(
        choices=[],  # Sẽ được cập nhật động
        required=True,
        label="Phương thức thanh toán"
    )

    def __init__(self, *args, **kwargs):
        payment_methods = kwargs.pop('payment_methods', [])
        super(PaymentForm, self).__init__(*args, **kwargs)

        # Cập nhật danh sách phương thức thanh toán
        self.fields['payment_method'].choices = [
            (method['id'], method['name'])
            for method in payment_methods
        ]


class OrderStatusForm(forms.Form):
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('processing', 'Đang xử lý'),
        ('shipped', 'Đã gửi hàng'),
        ('delivered', 'Đã giao hàng'),
        ('cancelled', 'Đã hủy'),
    ]

    status = forms.ChoiceField(choices=STATUS_CHOICES, required=True, label="Trạng thái")
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False, label="Ghi chú")


class OrderSearchForm(forms.Form):
    order_number = forms.CharField(required=False, label="Mã đơn hàng")
    status = forms.ChoiceField(
        choices=[('', '---')] + list(Order.STATUS_CHOICES),
        required=False,
        label="Trạng thái"
    )
    start_date = forms.DateField(required=False, label="Từ ngày", widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, label="Đến ngày", widget=forms.DateInput(attrs={'type': 'date'}))


class CancelOrderForm(forms.Form):
    REASON_CHOICES = [
        ('changed_mind', 'Tôi đổi ý'),
        ('found_better_price', 'Tìm thấy giá tốt hơn'),
        ('shipping_too_long', 'Thời gian giao hàng quá lâu'),
        ('ordering_mistake', 'Đặt nhầm sản phẩm'),
        ('other', 'Lý do khác'),
    ]

    reason = forms.ChoiceField(choices=REASON_CHOICES, required=True, label="Lý do hủy")
    other_reason = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False, label="Lý do khác")