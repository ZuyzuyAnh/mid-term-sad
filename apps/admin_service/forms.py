# apps/admin_service/forms.py
from django import forms
from .models import Banner, AIModel
import json


class UserForm(forms.Form):
    username = forms.CharField(max_length=150, required=True, label="Tên đăng nhập")
    email = forms.EmailField(required=True, label="Email")
    full_name = forms.CharField(max_length=255, required=True, label="Họ tên")
    is_active = forms.BooleanField(required=False, label="Đang hoạt động")
    is_staff = forms.BooleanField(required=False, label="Là nhân viên quản trị")


class VendorApprovalForm(forms.Form):
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label="Ghi chú"
    )


class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = [
            'title', 'image', 'link_url', 'position', 'start_date',
            'end_date', 'is_active', 'priority'
        ]
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class SystemConfigForm(forms.Form):
    site_name = forms.CharField(max_length=100, required=True, label="Tên trang web")
    site_description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        label="Mô tả trang web"
    )
    logo_url = forms.URLField(required=False, label="URL Logo")
    favicon_url = forms.URLField(required=False, label="URL Favicon")
    contact_email = forms.EmailField(required=True, label="Email liên hệ")
    support_phone = forms.CharField(max_length=20, required=True, label="Số điện thoại hỗ trợ")


class EmailSettingsForm(forms.Form):
    smtp_host = forms.CharField(max_length=100, required=True, label="SMTP Host")
    smtp_port = forms.IntegerField(required=True, label="SMTP Port")
    smtp_user = forms.CharField(max_length=100, required=True, label="SMTP User")
    smtp_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=True,
        label="SMTP Password"
    )
    email_from = forms.EmailField(required=True, label="Email gửi")
    email_reply_to = forms.EmailField(required=True, label="Email trả lời")


class PaymentSettingsForm(forms.Form):
    payment_methods = forms.MultipleChoiceField(
        choices=[
            ('cod', 'Thanh toán khi nhận hàng'),
            ('bank_transfer', 'Chuyển khoản ngân hàng'),
            ('credit_card', 'Thẻ tín dụng'),
            ('vnpay', 'VNPay'),
            ('momo', 'MoMo'),
            ('zalopay', 'ZaloPay'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Phương thức thanh toán"
    )
    currency = forms.CharField(max_length=3, required=True, label="Đơn vị tiền tệ", initial="VND")
    tax_rate = forms.DecimalField(required=True, label="Thuế suất (%)", initial=10)
    vnpay_merchant_id = forms.CharField(max_length=100, required=False, label="VNPay Merchant ID")
    vnpay_secret_key = forms.CharField(max_length=100, required=False, label="VNPay Secret Key")
    momo_partner_code = forms.CharField(max_length=100, required=False, label="MoMo Partner Code")
    momo_access_key = forms.CharField(max_length=100, required=False, label="MoMo Access Key")
    zalopay_app_id = forms.CharField(max_length=100, required=False, label="ZaloPay App ID")
    zalopay_key1 = forms.CharField(max_length=100, required=False, label="ZaloPay Key 1")


class ShippingSettingsForm(forms.Form):
    shipping_providers = forms.MultipleChoiceField(
        choices=[
            ('ghn', 'Giao Hàng Nhanh'),
            ('ghtk', 'Giao Hàng Tiết Kiệm'),
            ('viettel_post', 'Viettel Post'),
            ('vietnam_post', 'Vietnam Post'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Đơn vị vận chuyển"
    )
    free_shipping_threshold = forms.DecimalField(
        required=False,
        label="Ngưỡng miễn phí vận chuyển",
        help_text="Đơn hàng từ giá trị này trở lên sẽ được miễn phí vận chuyển. Để trống nếu không áp dụng."
    )
    default_shipping_fee = forms.DecimalField(
        required=True,
        label="Phí vận chuyển mặc định"
    )
    shipping_zones = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        label="Khu vực vận chuyển (JSON)",
        help_text="Định dạng JSON: [{'name': 'Miền Bắc', 'provinces': ['Hà Nội', 'Hải Phòng']}]"
    )

    def clean_shipping_zones(self):
        zones = self.cleaned_data.get('shipping_zones')
        if not zones:
            return []

        try:
            zones_data = json.loads(zones)
            return zones_data
        except json.JSONDecodeError:
            raise forms.ValidationError("Định dạng JSON không hợp lệ")


class PermissionForm(forms.Form):
    user_id = forms.IntegerField(required=True, label="ID người dùng")
    permissions = forms.MultipleChoiceField(
        choices=[],  # Sẽ được cập nhật động
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Quyền hạn"
    )

    def __init__(self, *args, **kwargs):
        permissions = kwargs.pop('permissions', [])
        super(PermissionForm, self).__init__(*args, **kwargs)

        # Cập nhật danh sách quyền
        self.fields['permissions'].choices = [
            (perm['id'], perm['name'])
            for perm in permissions
        ]


class AIModelForm(forms.ModelForm):
    class Meta:
        model = AIModel
        fields = [
            'name', 'model_type', 'version', 'description',
            'status', 'configuration'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'configuration': forms.Textarea(attrs={'rows': 5}),
        }