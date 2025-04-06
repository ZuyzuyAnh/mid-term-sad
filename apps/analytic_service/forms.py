# apps/analytic_service/forms.py
from django import forms
from datetime import datetime, timedelta


class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        required=True,
        label="Từ ngày",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        required=True,
        label="Đến ngày",
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    def __init__(self, *args, **kwargs):
        super(DateRangeForm, self).__init__(*args, **kwargs)
        # Set mặc định là 30 ngày gần nhất
        today = datetime.now().date()
        thirty_days_ago = today - timedelta(days=30)

        if not self.initial.get('start_date'):
            self.initial['start_date'] = thirty_days_ago
        if not self.initial.get('end_date'):
            self.initial['end_date'] = today

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("Ngày bắt đầu phải trước ngày kết thúc")

            # Giới hạn khoảng thời gian tối đa là 1 năm
            if end_date - start_date > timedelta(days=365):
                raise forms.ValidationError("Khoảng thời gian không được vượt quá 1 năm")

        return cleaned_data


class ReportForm(forms.Form):
    REPORT_TYPES = [
        ('sales', 'Báo cáo doanh số'),
        ('products', 'Hiệu suất sản phẩm'),
        ('customers', 'Phân tích khách hàng'),
        ('inventory', 'Báo cáo kho hàng'),
    ]

    PERIOD_CHOICES = [
        ('daily', 'Theo ngày'),
        ('weekly', 'Theo tuần'),
        ('monthly', 'Theo tháng'),
    ]

    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]

    report_type = forms.ChoiceField(
        choices=REPORT_TYPES,
        required=True,
        label="Loại báo cáo"
    )
    start_date = forms.DateField(
        required=True,
        label="Từ ngày",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        required=True,
        label="Đến ngày",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    period = forms.ChoiceField(
        choices=PERIOD_CHOICES,
        required=True,
        label="Phân chia theo"
    )
    format = forms.ChoiceField(
        choices=FORMAT_CHOICES,
        required=True,
        label="Định dạng"
    )
    include_charts = forms.BooleanField(
        required=False,
        initial=True,
        label="Bao gồm biểu đồ"
    )


class UserActivityFilterForm(forms.Form):
    ACTIVITY_TYPES = [
        ('', '---'),
        ('page_view', 'Xem trang'),
        ('product_view', 'Xem sản phẩm'),
        ('add_to_cart', 'Thêm vào giỏ hàng'),
        ('purchase', 'Mua hàng'),
        ('search', 'Tìm kiếm'),
    ]

    user_id = forms.IntegerField(required=False, label="ID người dùng")
    activity_type = forms.ChoiceField(
        choices=ACTIVITY_TYPES,
        required=False,
        label="Loại hoạt động"
    )
    start_date = forms.DateField(
        required=False,
        label="Từ ngày",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        label="Đến ngày",
        widget=forms.DateInput(attrs={'type': 'date'})
    )