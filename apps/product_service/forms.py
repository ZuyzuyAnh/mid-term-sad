# apps/product_service/forms.py
from django import forms
from .models import Category, Product, ProductImage, ProductAttribute, ProductAttributeValue, Inventory


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'parent', 'description', 'image', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ProductForm(forms.ModelForm):
    initial_quantity = forms.IntegerField(min_value=0, required=False, help_text="Số lượng ban đầu trong kho")

    class Meta:
        model = Product
        fields = [
            'name', 'category', 'description', 'short_description',
            'price', 'discount_price', 'status', 'featured'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'short_description': forms.Textarea(attrs={'rows': 2}),
        }


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'is_primary', 'alt_text']


class ProductAttributeForm(forms.ModelForm):
    class Meta:
        model = ProductAttribute
        fields = ['name', 'description']


class ProductAttributeValueForm(forms.ModelForm):
    class Meta:
        model = ProductAttributeValue
        fields = ['attribute', 'value']


class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['quantity', 'threshold_quantity']


class ProductSearchForm(forms.Form):
    query = forms.CharField(required=False, label="Tìm kiếm")
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(status=True),
        required=False,
        label="Danh mục"
    )
    min_price = forms.DecimalField(required=False, label="Giá thấp nhất")
    max_price = forms.DecimalField(required=False, label="Giá cao nhất")
    status = forms.ChoiceField(
        choices=[('', '---')] + list(Product.STATUS_CHOICES),
        required=False,
        label="Trạng thái"
    )