# apps/user_service/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import UserProfile, Address

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=255, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email đã được sử dụng')
        return email


class UserLoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('full_name', 'phone_number', 'birth_date', 'profile_picture')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = (
        'street_address', 'city', 'state', 'zip_code', 'country', 'address_type', 'is_default', 'phone_number')
        widgets = {
            'address_type': forms.Select(choices=Address.ADDRESS_TYPE_CHOICES),
        }


class VendorRegistrationForm(forms.Form):
    business_name = forms.CharField(max_length=255, required=True)
    business_description = forms.CharField(widget=forms.Textarea, required=True)
    tax_id = forms.CharField(max_length=50, required=True)
    phone_number = forms.CharField(max_length=20, required=True)
    website = forms.URLField(required=False)
    agree_terms = forms.BooleanField(required=True)