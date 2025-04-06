# apps/recommendation_service/forms.py
from django import forms
from .models import Review, ReviewResponse, UserPreference


class ReviewForm(forms.ModelForm):
    # Định nghĩa field này độc lập với model, không sử dụng attrs multiple
    images = forms.FileField(
        required=False,
        label="Hình ảnh",
        help_text="Chọn một hoặc nhiều hình ảnh (không bắt buộc)"
    )

    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_images(self):
        """Xử lý ở đây nếu cần kiểm tra thêm về hình ảnh"""
        return self.cleaned_data.get('images')


class ReviewResponseForm(forms.ModelForm):
    class Meta:
        model = ReviewResponse
        fields = ['response_text']
        widgets = {
            'response_text': forms.Textarea(attrs={'rows': 3}),
        }


class UserPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ['preferred_price_range', 'disliked_products']
        widgets = {
            'preferred_price_range': forms.TextInput(),  # Will be handled in JavaScript
            'disliked_products': forms.TextInput(),  # Will be handled in JavaScript
        }


class ProductRecommendationForm(forms.Form):
    RECOMMENDATION_TYPES = [
        ('personalized', 'Cá nhân hóa'),
        ('similar_products', 'Sản phẩm tương tự'),
        ('trending', 'Sản phẩm phổ biến'),
        ('top_rated', 'Đánh giá cao'),
    ]

    recommendation_type = forms.ChoiceField(
        choices=RECOMMENDATION_TYPES,
        required=True,
        label="Loại đề xuất"
    )
    limit = forms.IntegerField(
        min_value=1,
        max_value=50,
        initial=10,
        required=True,
        label="Số lượng sản phẩm"
    )