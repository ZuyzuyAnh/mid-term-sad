# apps/shipping_service/forms.py
from django import forms
from .models import ShippingMethod, ShippingZone, ZoneRate, Shipment, VendorShippingSettings


class ShippingMethodForm(forms.ModelForm):
    class Meta:
        model = ShippingMethod
        fields = ['name', 'description', 'price', 'estimated_days_min', 'estimated_days_max', 'is_active']


class ShippingZoneForm(forms.ModelForm):
    class Meta:
        model = ShippingZone
        fields = ['name', 'countries']
        widgets = {
            'countries': forms.SelectMultiple(),
        }


class ZoneRateForm(forms.ModelForm):
    class Meta:
        model = ZoneRate
        fields = ['zone', 'shipping_method', 'price']


class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = ['carrier', 'tracking_number', 'shipping_method', 'status', 'estimated_delivery']
        widgets = {
            'estimated_delivery': forms.DateInput(attrs={'type': 'date'}),
        }


class ShippingAddressForm(forms.Form):
    recipient_name = forms.CharField(max_length=255, required=True, label="Tên người nhận")
    phone_number = forms.CharField(max_length=20, required=True, label="Số điện thoại")
    street_address = forms.CharField(max_length=255, required=True, label="Địa chỉ")
    city = forms.CharField(max_length=100, required=True, label="Thành phố")
    state = forms.CharField(max_length=100, required=True, label="Tỉnh/Thành phố")
    zip_code = forms.CharField(max_length=20, required=True, label="Mã bưu điện")
    country = forms.CharField(max_length=100, required=True, label="Quốc gia")
    is_default = forms.BooleanField(required=False, label="Đặt làm địa chỉ mặc định")
    delivery_instructions = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False,
                                            label="Hướng dẫn giao hàng")


class ShippingSettingsForm(forms.ModelForm):
    class Meta:
        model = VendorShippingSettings
        fields = ['processing_time_days', 'free_shipping_threshold', 'shipping_policy', 'return_policy']
        widgets = {
            'shipping_policy': forms.Textarea(attrs={'rows': 4}),
            'return_policy': forms.Textarea(attrs={'rows': 4}),
        }


class TrackingUpdateForm(forms.Form):
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('processing', 'Đang xử lý'),
        ('shipped', 'Đã gửi hàng'),
        ('in_transit', 'Đang vận chuyển'),
        ('delivered', 'Đã giao hàng'),
        ('failed', 'Giao hàng không thành công'),
        ('returned', 'Trả lại người gửi'),
    ]

    status = forms.ChoiceField(choices=STATUS_CHOICES, required=True, label="Trạng thái")
    location = forms.CharField(max_length=255, required=True, label="Vị trí")
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False, label="Mô tả")