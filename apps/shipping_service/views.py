# apps/shipping_service/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
import requests
from .models import (
    ShippingMethod, ShippingZone, ZoneRate, Shipment,
    TrackingInfo, VendorShippingSettings
)
from .serializers import ShippingMethodSerializer, ShipmentSerializer
from .forms import ShippingAddressForm, ShippingSettingsForm


def shipping_methods(request):
    """Hiển thị danh sách phương thức vận chuyển"""
    methods = ShippingMethod.objects.filter(is_active=True)
    return render(request, 'shipping_service/shipping_methods.html', {'methods': methods})


@api_view(['POST'])
def calculate_shipping(request):
    """Tính toán chi phí vận chuyển"""
    data = request.data
    address = data.get('address', {})
    products = data.get('products', [])

    # Xác định zone dựa trên địa chỉ
    country = address.get('country', '')
    zone = ShippingZone.objects.filter(countries__contains=[country]).first()

    if not zone:
        return Response({'error': 'Không hỗ trợ vận chuyển đến khu vực này'}, status=400)

    # Lấy các phương thức vận chuyển khả dụng cho zone
    zone_rates = ZoneRate.objects.filter(zone=zone).select_related('shipping_method')

    # Tính toán chi phí vận chuyển cho từng phương thức
    result = []
    for zone_rate in zone_rates:
        method = zone_rate.shipping_method
        if method.is_active:
            result.append({
                'method_id': method.id,
                'name': method.name,
                'description': method.description,
                'price': float(zone_rate.price),
                'estimated_days_min': method.estimated_days_min,
                'estimated_days_max': method.estimated_days_max,
            })

    return Response(result)


def track_shipment(request, tracking_number):
    """Theo dõi trạng thái vận chuyển"""
    try:
        shipment = Shipment.objects.get(tracking_number=tracking_number)
        tracking_info = shipment.tracking_info.all().order_by('-timestamp')

        context = {
            'shipment': shipment,
            'tracking_info': tracking_info,
        }
        return render(request, 'shipping_service/track_shipment.html', context)
    except Shipment.DoesNotExist:
        messages.error(request, "Không tìm thấy thông tin vận chuyển với mã theo dõi này!")
        return render(request, 'shipping_service/track_shipment_form.html')


def shipment_details(request, order_id):
    """Chi tiết vận chuyển của đơn hàng"""
    try:
        shipment = Shipment.objects.get(order_id=order_id)
        tracking_info = shipment.tracking_info.all().order_by('-timestamp')

        context = {
            'shipment': shipment,
            'tracking_info': tracking_info,
        }
        return render(request, 'shipping_service/shipment_details.html', context)
    except Shipment.DoesNotExist:
        messages.error(request, "Không tìm thấy thông tin vận chuyển cho đơn hàng này!")
        return redirect('order_service:order_detail', pk=order_id)


@api_view(['POST'])
def validate_address(request):
    """Kiểm tra tính hợp lệ của địa chỉ"""
    data = request.data
    # TODO: Tích hợp với API kiểm tra địa chỉ bên thứ ba

    # Giả lập kiểm tra đơn giản
    required_fields = ['street_address', 'city', 'state', 'zip_code', 'country']
    errors = {}

    for field in required_fields:
        if not data.get(field):
            errors[field] = f"Trường {field} là bắt buộc"

    if errors:
        return Response({'valid': False, 'errors': errors})
    return Response({'valid': True})


@login_required
def vendor_shipments(request):
    """Danh sách đơn vận chuyển của người bán"""
    # Lấy thông tin vendor_id
    vendor_id = request.user.id

    # TODO: Lấy danh sách đơn hàng của vendor từ Order Service
    order_ids = []  # Giả định danh sách order_id

    # Lấy các đơn vận chuyển
    shipments = Shipment.objects.filter(order_id__in=order_ids).order_by('-created_at')

    # Lọc theo trạng thái
    status = request.GET.get('status')
    if status:
        shipments = shipments.filter(status=status)

    # Phân trang
    paginator = Paginator(shipments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status,
    }
    return render(request, 'shipping_service/vendor/shipments.html', context)


@login_required
def update_shipment(request, pk):
    """Cập nhật trạng thái vận chuyển"""
    # Lấy thông tin vendor_id
    vendor_id = request.user.id

    # TODO: Xác thực quyền truy cập
    shipment = get_object_or_404(Shipment, pk=pk)

    if request.method == 'POST':
        status = request.POST.get('status')
        location = request.POST.get('location', '')
        description = request.POST.get('description', '')

        # Cập nhật trạng thái shipment
        shipment.status = status
        shipment.save()

        # Thêm thông tin tracking mới
        TrackingInfo.objects.create(
            shipment=shipment,
            status=status,
            location=location,
            description=description,
            timestamp=timezone.now()
        )

        # Cập nhật trạng thái đơn hàng
        # TODO: Gửi request đến Order Service để cập nhật trạng thái

        messages.success(request, "Đã cập nhật trạng thái vận chuyển!")
        return redirect('shipping_service:vendor_shipments')

    return render(request, 'shipping_service/vendor/update_shipment.html', {'shipment': shipment})


@login_required
def vendor_shipping_settings(request):
    """Quản lý cài đặt vận chuyển của người bán"""
    vendor_id = request.user.id

    settings, created = VendorShippingSettings.objects.get_or_create(vendor_id=vendor_id)
    available_methods = ShippingMethod.objects.filter(is_active=True)

    if request.method == 'POST':
        form = ShippingSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()

            # Cập nhật các phương thức vận chuyển
            selected_methods = request.POST.getlist('available_shipping_methods')
            settings.available_shipping_methods.clear()
            for method_id in selected_methods:
                settings.available_shipping_methods.add(method_id)

            messages.success(request, "Đã cập nhật cài đặt vận chuyển!")
            return redirect('shipping_service:vendor_shipping_settings')
        else:
            messages.error(request, "Cập nhật không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = ShippingSettingsForm(instance=settings)

    context = {
        'form': form,
        'settings': settings,
        'available_methods': available_methods,
    }
    return render(request, 'shipping_service/vendor/shipping_settings.html', context)


def shipping_zones(request):
    """Danh sách khu vực vận chuyển"""
    zones = ShippingZone.objects.all()
    return render(request, 'shipping_service/zones.html', {'zones': zones})


def shipping_zone_detail(request, pk):
    """Chi tiết khu vực vận chuyển"""
    zone = get_object_or_404(ShippingZone, pk=pk)
    rates = zone.rates.all().select_related('shipping_method')

    context = {
        'zone': zone,
        'rates': rates,
    }
    return render(request, 'shipping_service/zone_detail.html', context)


@api_view(['GET'])
def get_shipping_options(request, order_id):
    """API endpoint để lấy các lựa chọn vận chuyển cho đơn hàng"""
    # TODO: Lấy thông tin đơn hàng từ Order Service

    # Giả định dữ liệu
    country = 'VN'

    # Xác định zone
    zone = ShippingZone.objects.filter(countries__contains=[country]).first()

    if not zone:
        return Response({'error': 'Không hỗ trợ vận chuyển đến khu vực này'}, status=400)

    # Lấy phương thức vận chuyển
    zone_rates = ZoneRate.objects.filter(zone=zone).select_related('shipping_method')

    options = []
    for zone_rate in zone_rates:
        method = zone_rate.shipping_method
        if method.is_active:
            options.append({
                'method_id': method.id,
                'name': method.name,
                'description': method.description,
                'price': float(zone_rate.price),
                'estimated_days_min': method.estimated_days_min,
                'estimated_days_max': method.estimated_days_max,
            })

    return Response(options)


@api_view(['POST'])
def generate_shipping_label(request, shipment_id):
    """API endpoint để tạo nhãn vận chuyển"""
    try:
        shipment = Shipment.objects.get(id=shipment_id)
    except Shipment.DoesNotExist:
        return Response({'error': 'Shipment not found'}, status=404)

    # TODO: Tích hợp với API bên thứ ba để tạo nhãn vận chuyển

    # Giả lập
    label_url = f"https://example.com/shipping-labels/{shipment.tracking_number}.pdf"

    return Response({'label_url': label_url})