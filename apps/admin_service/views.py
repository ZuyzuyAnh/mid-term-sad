# apps/admin_service/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
import requests
from .models import (
    AdminSettings, SystemConfiguration, AuditLog,
    Banner, NotificationSetting, AIModel
)
from .serializers import SystemConfigurationSerializer, AuditLogSerializer
from .forms import (
    UserForm, VendorApprovalForm, BannerForm, SystemConfigForm,
    EmailSettingsForm, PaymentSettingsForm, ShippingSettingsForm,
    PermissionForm, AIModelForm
)


def is_admin(user):
    """Kiểm tra xem người dùng có phải là admin không"""
    return user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Bảng điều khiển admin"""
    # Thống kê người dùng
    # TODO: Lấy từ User Service
    user_count = 0

    # Thống kê đơn hàng
    # TODO: Lấy từ Order Service
    order_count = 0

    # Thống kê doanh thu
    # TODO: Lấy từ Order Service
    total_revenue = 0

    # Lấy nhật ký hệ thống gần đây
    recent_logs = AuditLog.objects.all().order_by('-timestamp')[:10]

    context = {
        'user_count': user_count,
        'order_count': order_count,
        'total_revenue': total_revenue,
        'recent_logs': recent_logs,
    }
    return render(request, 'admin_service/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def user_management(request):
    """Quản lý người dùng"""
    # Lấy danh sách người dùng từ User Service
    # TODO: Thay thế bằng API call thực tế
    users = []

    # Tìm kiếm
    query = request.GET.get('q')
    if query:
        # TODO: Tìm kiếm người dùng
        pass

    # Lọc theo loại
    user_type = request.GET.get('type')
    if user_type:
        # TODO: Lọc theo loại người dùng
        pass

    # Phân trang
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'user_type': user_type,
    }
    return render(request, 'admin_service/user_management.html', context)


@login_required
@user_passes_test(is_admin)
def user_details(request, pk):
    """Chi tiết người dùng"""
    # Lấy thông tin người dùng từ User Service
    # TODO: Thay thế bằng API call thực tế
    user_data = {}

    # Lấy lịch sử đơn hàng từ Order Service
    # TODO: Thay thế bằng API call thực tế
    order_history = []

    context = {
        'user': user_data,
        'order_history': order_history,
    }
    return render(request, 'admin_service/user_details.html', context)


@login_required
@user_passes_test(is_admin)
def update_user(request, pk):
    """Cập nhật thông tin người dùng"""
    # Lấy thông tin người dùng từ User Service
    # TODO: Thay thế bằng API call thực tế
    user_data = {}

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # TODO: Cập nhật thông tin người dùng

            messages.success(request, "Thông tin người dùng đã được cập nhật!")
            return redirect('admin_service:user_details', pk=pk)
        else:
            messages.error(request, "Cập nhật không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = UserForm(initial=user_data)

    context = {
        'form': form,
        'user': user_data,
    }
    return render(request, 'admin_service/update_user.html', context)


@login_required
@user_passes_test(is_admin)
@require_POST
def delete_user(request, pk):
    """Xóa người dùng"""
    # TODO: Gọi API User Service để xóa người dùng

    messages.success(request, "Người dùng đã được xóa!")
    return redirect('admin_service:user_management')


@login_required
@user_passes_test(is_admin)
def vendor_management(request):
    """Quản lý người bán"""
    # Lấy danh sách người bán từ User Service
    # TODO: Thay thế bằng API call thực tế
    vendors = []

    # Tìm kiếm
    query = request.GET.get('q')
    if query:
        # TODO: Tìm kiếm người bán
        pass

    # Lọc theo trạng thái
    status = request.GET.get('status')
    if status:
        # TODO: Lọc theo trạng thái
        pass

    # Phân trang
    paginator = Paginator(vendors, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'status': status,
    }
    return render(request, 'admin_service/vendor_management.html', context)


@login_required
@user_passes_test(is_admin)
def pending_vendors(request):
    """Danh sách người bán chờ phê duyệt"""
    # Lấy danh sách người bán chờ phê duyệt từ User Service
    # TODO: Thay thế bằng API call thực tế
    pending_vendors = []

    # Phân trang
    paginator = Paginator(pending_vendors, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'admin_service/pending_vendors.html', context)


@login_required
@user_passes_test(is_admin)
def approve_vendor(request, pk):
    """Phê duyệt người bán"""
    if request.method == 'POST':
        form = VendorApprovalForm(request.POST)
        if form.is_valid():
            # TODO: Gọi API User Service để phê duyệt người bán

            messages.success(request, "Đã phê duyệt người bán!")
            return redirect('admin_service:pending_vendors')
        else:
            messages.error(request, "Phê duyệt không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = VendorApprovalForm()

    # Lấy thông tin người bán
    # TODO: Thay thế bằng API call thực tế
    vendor_data = {}

    context = {
        'form': form,
        'vendor': vendor_data,
    }
    return render(request, 'admin_service/approve_vendor.html', context)


@login_required
@user_passes_test(is_admin)
@require_POST
def decline_vendor(request, pk):
    """Từ chối người bán"""
    reason = request.POST.get('reason', '')

    # TODO: Gọi API User Service để từ chối người bán

    messages.success(request, "Đã từ chối đăng ký người bán!")
    return redirect('admin_service:pending_vendors')


@login_required
@user_passes_test(is_admin)
def content_management(request):
    """Quản lý nội dung"""
    return render(request, 'admin_service/content_management.html')


@login_required
@user_passes_test(is_admin)
def manage_banners(request):
    """Quản lý banner"""
    banners = Banner.objects.all().order_by('-priority', '-start_date')

    # Lọc theo vị trí
    position = request.GET.get('position')
    if position:
        banners = banners.filter(position=position)

    # Lọc theo trạng thái
    is_active = request.GET.get('is_active')
    if is_active is not None:
        banners = banners.filter(is_active=is_active == 'true')

    # Phân trang
    paginator = Paginator(banners, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'position_filter': position,
        'is_active_filter': is_active,
    }
    return render(request, 'admin_service/manage_banners.html', context)


@login_required
@user_passes_test(is_admin)
def add_banner(request):
    """Thêm banner mới"""
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            banner = form.save(commit=False)
            banner.created_by = request.user.id
            banner.save()

            messages.success(request, "Đã thêm banner mới!")
            return redirect('admin_service:manage_banners')
        else:
            messages.error(request, "Thêm banner không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = BannerForm()

    return render(request, 'admin_service/add_banner.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def update_banner(request, pk):
    """Cập nhật banner"""
    banner = get_object_or_404(Banner, pk=pk)

    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()

            messages.success(request, "Đã cập nhật banner!")
            return redirect('admin_service:manage_banners')
        else:
            messages.error(request, "Cập nhật banner không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = BannerForm(instance=banner)

    return render(request, 'admin_service/update_banner.html', {'form': form, 'banner': banner})


@login_required
@user_passes_test(is_admin)
@require_POST
def delete_banner(request, pk):
    """Xóa banner"""
    banner = get_object_or_404(Banner, pk=pk)
    banner.delete()

    messages.success(request, "Đã xóa banner!")
    return redirect('admin_service:manage_banners')


@login_required
@user_passes_test(is_admin)
def system_configuration(request):
    """Trang quản lý cấu hình hệ thống"""
    return render(request, 'admin_service/system_configuration.html')


@login_required
@user_passes_test(is_admin)
def general_settings(request):
    """Cài đặt chung của hệ thống"""
    # Lấy cài đặt hiện tại
    configs = SystemConfiguration.objects.filter(
        setting_name__in=[
            'site_name', 'site_description', 'logo_url',
            'favicon_url', 'contact_email', 'support_phone'
        ]
    )

    # Tạo dictionary từ cài đặt
    current_settings = {config.setting_name: config.setting_value for config in configs}

    if request.method == 'POST':
        form = SystemConfigForm(request.POST)
        if form.is_valid():
            # Cập nhật các cài đặt
            for key, value in form.cleaned_data.items():
                SystemConfiguration.objects.update_or_create(
                    setting_name=key,
                    defaults={
                        'setting_value': value,
                        'data_type': 'string',
                    }
                )

            # Ghi log
            AuditLog.objects.create(
                user_id=request.user.id,
                action='update_general_settings',
                details={},
                ip_address=request.META.get('REMOTE_ADDR'),
                service_name='admin_service',
            )

            messages.success(request, "Đã cập nhật cài đặt hệ thống!")
            return redirect('admin_service:general_settings')
        else:
            messages.error(request, "Cập nhật không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = SystemConfigForm(initial=current_settings)

    context = {
        'form': form,
    }
    return render(request, 'admin_service/general_settings.html', context)


@login_required
@user_passes_test(is_admin)
def email_settings(request):
    """Cài đặt email"""
    # Lấy cài đặt hiện tại
    configs = SystemConfiguration.objects.filter(
        setting_name__in=[
            'smtp_host', 'smtp_port', 'smtp_user',
            'smtp_password', 'email_from', 'email_reply_to'
        ]
    )

    # Tạo dictionary từ cài đặt
    current_settings = {config.setting_name: config.setting_value for config in configs}

    if request.method == 'POST':
        form = EmailSettingsForm(request.POST)
        if form.is_valid():
            # Cập nhật các cài đặt
            for key, value in form.cleaned_data.items():
                SystemConfiguration.objects.update_or_create(
                    setting_name=key,
                    defaults={
                        'setting_value': value,
                        'data_type': 'string' if key != 'smtp_port' else 'integer',
                    }
                )

            # Ghi log
            AuditLog.objects.create(
                user_id=request.user.id,
                action='update_email_settings',
                details={},
                ip_address=request.META.get('REMOTE_ADDR'),
                service_name='admin_service',
            )

            messages.success(request, "Đã cập nhật cài đặt email!")
            return redirect('admin_service:email_settings')
        else:
            messages.error(request, "Cập nhật không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = EmailSettingsForm(initial=current_settings)

    context = {
        'form': form,
    }
    return render(request, 'admin_service/email_settings.html', context)


@login_required
@user_passes_test(is_admin)
def payment_settings(request):
    """Cài đặt thanh toán"""
    # Lấy cài đặt hiện tại
    configs = SystemConfiguration.objects.filter(
        setting_name__in=[
            'payment_methods', 'currency', 'tax_rate',
            'vnpay_merchant_id', 'vnpay_secret_key',
            'momo_partner_code', 'momo_access_key',
            'zalopay_app_id', 'zalopay_key1'
        ]
    )

    # Tạo dictionary từ cài đặt
    current_settings = {config.setting_name: config.setting_value for config in configs}

    if request.method == 'POST':
        form = PaymentSettingsForm(request.POST)
        if form.is_valid():
            # Cập nhật các cài đặt
            for key, value in form.cleaned_data.items():
                data_type = 'string'
                if key == 'tax_rate':
                    data_type = 'float'
                elif key == 'payment_methods':
                    data_type = 'json'
                    value = json.dumps(value)

                SystemConfiguration.objects.update_or_create(
                    setting_name=key,
                    defaults={
                        'setting_value': value,
                        'data_type': data_type,
                    }
                )

            # Ghi log
            AuditLog.objects.create(
                user_id=request.user.id,
                action='update_payment_settings',
                details={},
                ip_address=request.META.get('REMOTE_ADDR'),
                service_name='admin_service',
            )

            messages.success(request, "Đã cập nhật cài đặt thanh toán!")
            return redirect('admin_service:payment_settings')
        else:
            messages.error(request, "Cập nhật không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        # Xử lý dữ liệu json
        if 'payment_methods' in current_settings:
            try:
                current_settings['payment_methods'] = json.loads(current_settings['payment_methods'])
            except:
                current_settings['payment_methods'] = []

        form = PaymentSettingsForm(initial=current_settings)

    context = {
        'form': form,
    }
    return render(request, 'admin_service/payment_settings.html', context)


@login_required
@user_passes_test(is_admin)
def shipping_settings(request):
    """Cài đặt vận chuyển"""
    # Lấy cài đặt hiện tại
    configs = SystemConfiguration.objects.filter(
        setting_name__in=[
            'shipping_providers', 'free_shipping_threshold',
            'default_shipping_fee', 'shipping_zones'
        ]
    )

    # Tạo dictionary từ cài đặt
    current_settings = {config.setting_name: config.setting_value for config in configs}

    if request.method == 'POST':
        form = ShippingSettingsForm(request.POST)
        if form.is_valid():
            # Cập nhật các cài đặt
            for key, value in form.cleaned_data.items():
                data_type = 'string'
                if key in ['free_shipping_threshold', 'default_shipping_fee']:
                    data_type = 'float'
                elif key in ['shipping_providers', 'shipping_zones']:
                    data_type = 'json'
                    value = json.dumps(value)

                SystemConfiguration.objects.update_or_create(
                    setting_name=key,
                    defaults={
                        'setting_value': value,
                        'data_type': data_type,
                    }
                )

            # Ghi log
            AuditLog.objects.create(
                user_id=request.user.id,
                action='update_shipping_settings',
                details={},
                ip_address=request.META.get('REMOTE_ADDR'),
                service_name='admin_service',
            )

            messages.success(request, "Đã cập nhật cài đặt vận chuyển!")
            return redirect('admin_service:shipping_settings')
        else:
            messages.error(request, "Cập nhật không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        # Xử lý dữ liệu json
        for key in ['shipping_providers', 'shipping_zones']:
            if key in current_settings:
                try:
                    current_settings[key] = json.loads(current_settings[key])
                except:
                    current_settings[key] = []

        form = ShippingSettingsForm(initial=current_settings)

    context = {
        'form': form,
    }
    return render(request, 'admin_service/shipping_settings.html', context)


@login_required
@user_passes_test(is_admin)
def security_management(request):
    """Quản lý bảo mật"""
    return render(request, 'admin_service/security_management.html')


@login_required
@user_passes_test(is_admin)
def audit_logs(request):
    """Nhật ký hoạt động hệ thống"""
    logs = AuditLog.objects.all().order_by('-timestamp')

    # Lọc theo user
    user_id = request.GET.get('user_id')
    if user_id:
        logs = logs.filter(user_id=user_id)

    # Lọc theo action
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)

    # Lọc theo service
    service = request.GET.get('service')
    if service:
        logs = logs.filter(service_name=service)

    # Lọc theo thời gian
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d').replace(
                hour=0, minute=0, second=0
            )
            logs = logs.filter(timestamp__gte=start_datetime)
        except ValueError:
            pass

    if end_date:
        try:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d').replace(
                hour=23, minute=59, second=59
            )
            logs = logs.filter(timestamp__lte=end_datetime)
        except ValueError:
            pass

    # Phân trang
    paginator = Paginator(logs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'user_id_filter': user_id,
        'action_filter': action,
        'service_filter': service,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'admin_service/audit_logs.html', context)


@login_required
@user_passes_test(is_admin)
def manage_permissions(request):
    """Quản lý phân quyền"""
    # TODO: Lấy danh sách người dùng và quyền

    if request.method == 'POST':
        form = PermissionForm(request.POST)
        if form.is_valid():
            # TODO: Cập nhật quyền

            messages.success(request, "Đã cập nhật phân quyền!")
            return redirect('admin_service:manage_permissions')
        else:
            messages.error(request, "Cập nhật không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = PermissionForm()

    context = {
        'form': form,
    }
    return render(request, 'admin_service/manage_permissions.html', context)


@login_required
@user_passes_test(is_admin)
def ai_models(request):
    """Quản lý các model AI"""
    models = AIModel.objects.all().order_by('model_type', '-version')

    # Lọc theo loại model
    model_type = request.GET.get('type')
    if model_type:
        models = models.filter(model_type=model_type)

    # Lọc theo trạng thái
    status = request.GET.get('status')
    if status:
        models = models.filter(status=status)

    # Phân trang
    paginator = Paginator(models, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'type_filter': model_type,
        'status_filter': status,
    }
    return render(request, 'admin_service/ai_models.html', context)


@login_required
@user_passes_test(is_admin)
def update_ai_model(request, pk):
    """Cập nhật model AI"""
    model = get_object_or_404(AIModel, pk=pk)

    if request.method == 'POST':
        form = AIModelForm(request.POST, instance=model)
        if form.is_valid():
            form.save()

            # Ghi log
            AuditLog.objects.create(
                user_id=request.user.id,
                action='update_ai_model',
                details={'model_id': model.id, 'model_name': model.name},
                ip_address=request.META.get('REMOTE_ADDR'),
                service_name='admin_service',
            )

            messages.success(request, "Đã cập nhật model AI!")
            return redirect('admin_service:ai_models')
        else:
            messages.error(request, "Cập nhật không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = AIModelForm(instance=model)

    context = {
        'form': form,
        'model': model,
    }
    return render(request, 'admin_service/update_ai_model.html', context)


@login_required
@user_passes_test(is_admin)
def train_ai_model(request, model_type):
    """Huấn luyện model AI"""
    # TODO: Triển khai logic huấn luyện AI

    messages.success(request, f"Đã bắt đầu huấn luyện model AI loại {model_type}!")
    return redirect('admin_service:ai_models')


@api_view(['GET'])
def system_health(request):
    """API endpoint để kiểm tra sức khỏe hệ thống"""
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({'error': 'Unauthorized'}, status=401)

    # Kiểm tra kết nối đến các service
    services_status = {}

    # TODO: Kiểm tra kết nối đến các service khác
    # Ví dụ:
    services_status['user_service'] = 'ok'
    services_status['product_service'] = 'ok'
    services_status['order_service'] = 'ok'
    services_status['payment_service'] = 'ok'
    services_status['shipping_service'] = 'ok'
    services_status['recommendation_service'] = 'ok'
    services_status['analytic_service'] = 'ok'

    # Kiểm tra kết nối đến database
    db_status = 'ok'
    try:
        # Thử truy vấn database
        AdminSettings.objects.first()
    except Exception as e:
        db_status = f'error: {str(e)}'

    return Response({
        'status': 'ok',
        'services': services_status,
        'database': db_status,
        'timestamp': timezone.now(),
    })


# apps/admin_service/views.py (tiếp)
@api_view(['POST'])
def create_backup(request):
    """API endpoint để tạo backup dữ liệu"""
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({'error': 'Unauthorized'}, status=401)

    # TODO: Triển khai logic backup

    # Ghi log
    AuditLog.objects.create(
        user_id=request.user.id,
        action='create_backup',
        details={},
        ip_address=request.META.get('REMOTE_ADDR'),
        service_name='admin_service',
    )

    backup_id = f"backup_{timezone.now().strftime('%Y%m%d%H%M%S')}"

    return Response({
        'success': True,
        'backup_id': backup_id,
        'timestamp': timezone.now(),
        'message': 'Backup đã được tạo thành công!',
    })