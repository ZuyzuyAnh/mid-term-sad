# apps/user_service/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import User, UserProfile, Address, UserPermission
from .serializers import UserSerializer, AddressSerializer
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, AddressForm, VendorRegistrationForm
import uuid
import json

User = get_user_model()


def register_user(request):
    """Đăng ký người dùng mới"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Tạo user profile
            UserProfile.objects.create(user=user, full_name=form.cleaned_data.get('full_name', ''))
            login(request, user)
            messages.success(request, "Đăng ký tài khoản thành công!")
            return redirect('user_service:profile')
        else:
            messages.error(request, "Đăng ký không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = UserRegistrationForm()
    return render(request, 'user_service/register.html', {'form': form})


def login_user(request):
    """Đăng nhập người dùng"""
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                user.last_login = timezone.now()
                user.save()
                messages.success(request, "Đăng nhập thành công!")
                next_url = request.GET.get('next', 'user_service:profile')
                return redirect(next_url)
            else:
                messages.error(request, "Email hoặc mật khẩu không chính xác.")
        else:
            messages.error(request, "Đăng nhập không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = UserLoginForm()
    return render(request, 'user_service/login.html', {'form': form})


@login_required
def logout_user(request):
    """Đăng xuất người dùng"""
    logout(request)
    messages.success(request, "Bạn đã đăng xuất thành công!")
    return redirect('user_service:login')


def password_reset(request):
    """Khởi tạo quy trình đặt lại mật khẩu"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Tạo token và gửi email
            token = str(uuid.uuid4())
            # Lưu token vào session hoặc database
            # TODO: Gửi email với link reset password kèm token
            messages.success(request,
                             "Email hướng dẫn đặt lại mật khẩu đã được gửi. Vui lòng kiểm tra hộp thư của bạn.")
            return redirect('user_service:login')
        except User.DoesNotExist:
            messages.error(request, "Không tìm thấy tài khoản với email này.")
    return render(request, 'user_service/password_reset.html')


def password_reset_confirm(request, token):
    """Xác nhận đặt lại mật khẩu với token"""
    # TODO: Kiểm tra token hợp lệ
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password == confirm_password:
            # TODO: Cập nhật mật khẩu
            messages.success(request, "Mật khẩu đã được đặt lại thành công. Bạn có thể đăng nhập với mật khẩu mới.")
            return redirect('user_service:login')
        else:
            messages.error(request, "Mật khẩu không khớp.")
    return render(request, 'user_service/password_reset_confirm.html')


@login_required
def user_profile(request):
    """Xem thông tin profile người dùng"""
    profile = UserProfile.objects.get_or_create(user=request.user)[0]
    addresses = Address.objects.filter(user=request.user)
    default_address = addresses.filter(is_default=True).first()

    context = {
        'user': request.user,
        'profile': profile,
        'addresses': addresses,
        'default_address': default_address,
    }
    return render(request, 'user_service/profile.html', context)


@login_required
def update_profile(request):
    """Cập nhật thông tin profile"""
    profile = UserProfile.objects.get_or_create(user=request.user)[0]

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Thông tin cá nhân đã được cập nhật!")
            return redirect('user_service:profile')
        else:
            messages.error(request, "Cập nhật không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'user_service/update_profile.html', {'form': form})


@login_required
def address_list(request):
    """Danh sách địa chỉ của người dùng"""
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'user_service/address_list.html', {'addresses': addresses})


@login_required
def add_address(request):
    """Thêm địa chỉ mới"""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            if form.cleaned_data.get('is_default'):
                # Đảm bảo chỉ có một địa chỉ mặc định
                Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
                address.is_default = True
            address.save()
            messages.success(request, "Đã thêm địa chỉ mới!")
            return redirect('user_service:address_list')
        else:
            messages.error(request, "Thêm địa chỉ không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = AddressForm()

    return render(request, 'user_service/add_address.html', {'form': form})


@login_required
def update_address(request, pk):
    """Cập nhật địa chỉ"""
    address = get_object_or_404(Address, pk=pk, user=request.user)

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            updated_address = form.save(commit=False)
            if form.cleaned_data.get('is_default'):
                # Đảm bảo chỉ có một địa chỉ mặc định
                Address.objects.filter(user=request.user, is_default=True).exclude(pk=pk).update(is_default=False)
                updated_address.is_default = True
            updated_address.save()
            messages.success(request, "Địa chỉ đã được cập nhật!")
            return redirect('user_service:address_list')
        else:
            messages.error(request, "Cập nhật địa chỉ không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = AddressForm(instance=address)

    return render(request, 'user_service/update_address.html', {'form': form})


@login_required
def delete_address(request, pk):
    """Xóa địa chỉ"""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        is_default = address.is_default
        address.delete()
        # Nếu xóa địa chỉ mặc định, đặt địa chỉ đầu tiên làm mặc định
        if is_default:
            first_address = Address.objects.filter(user=request.user).first()
            if first_address:
                first_address.is_default = True
                first_address.save()
        messages.success(request, "Địa chỉ đã được xóa!")
        return redirect('user_service:address_list')
    return render(request, 'user_service/delete_address.html', {'address': address})


@login_required
def set_default_address(request, pk):
    """Đặt địa chỉ mặc định"""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
    address.is_default = True
    address.save()
    messages.success(request, "Đã đặt địa chỉ mặc định mới!")
    return redirect('user_service:address_list')


@login_required
def vendor_register(request):
    """Đăng ký làm người bán"""
    # Kiểm tra xem người dùng đã là vendor chưa
    profile = UserProfile.objects.get_or_create(user=request.user)[0]
    if profile.is_vendor:
        messages.info(request, "Bạn đã đăng ký làm người bán.")
        return redirect('user_service:vendor_profile')

    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                profile.is_vendor = True
                profile.vendor_approved = False  # Chờ admin phê duyệt
                profile.save()
                # TODO: Lưu thông tin đăng ký người bán
                messages.success(request, "Đăng ký làm người bán thành công! Yêu cầu của bạn đang được xử lý.")
                return redirect('user_service:profile')
        else:
            messages.error(request, "Đăng ký không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = VendorRegistrationForm()

    return render(request, 'user_service/vendor_register.html', {'form': form})


@login_required
def vendor_profile(request):
    """Xem profile người bán"""
    profile = UserProfile.objects.get_or_create(user=request.user)[0]
    if not profile.is_vendor:
        messages.warning(request, "Bạn chưa đăng ký làm người bán.")
        return redirect('user_service:vendor_register')

    # TODO: Lấy thông tin người bán
    context = {
        'profile': profile,
    }
    return render(request, 'user_service/vendor_profile.html', context)


@login_required
def update_vendor_profile(request):
    """Cập nhật thông tin người bán"""
    profile = UserProfile.objects.get_or_create(user=request.user)[0]
    if not profile.is_vendor:
        messages.warning(request, "Bạn chưa đăng ký làm người bán.")
        return redirect('user_service:vendor_register')

    # TODO: Cập nhật thông tin người bán
    if request.method == 'POST':
        # TODO: Xử lý form cập nhật thông tin
        messages.success(request, "Thông tin người bán đã được cập nhật!")
        return redirect('user_service:vendor_profile')

    # TODO: Hiển thị form
    return render(request, 'user_service/update_vendor_profile.html')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_api(request):
    """API endpoint để lấy thông tin người dùng hiện tại"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
def check_email_exists(request):
    """API endpoint để kiểm tra email đã tồn tại chưa"""
    email = request.data.get('email', '')
    exists = User.objects.filter(email=email).exists()
    return Response({'exists': exists})


@api_view(['POST'])
def check_username_exists(request):
    """API endpoint để kiểm tra username đã tồn tại chưa"""
    username = request.data.get('username', '')
    exists = User.objects.filter(username=username).exists()
    return Response({'exists': exists})