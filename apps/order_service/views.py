# apps/order_service/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Sum, F
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
import requests
import json
import uuid
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Cart, CartItem, Order, OrderItem, OrderStatusHistory, Wishlist, WishlistItem
from .serializers import CartSerializer, OrderSerializer
from .forms import OrderForm, ShippingForm


# apps/order_service/views.py (tiếp)
def _get_or_create_cart(request):
    """Helper function để lấy hoặc tạo giỏ hàng"""
    if request.user.is_authenticated:
        # Tìm giỏ hàng đang hoạt động của user
        cart = Cart.objects.filter(user_id=request.user.id, status='active').first()

        # Nếu có session_id, kiểm tra cart cho session đó và merge nếu cần
        session_id = request.session.get('cart_session_id')
        if session_id:
            session_cart = Cart.objects.filter(session_id=session_id, status='active').first()
            if session_cart:
                if cart:
                    # Merge giỏ hàng từ session vào giỏ hàng của user
                    for item in session_cart.items.all():
                        cart_item, created = CartItem.objects.get_or_create(
                            cart=cart,
                            product_id=item.product_id,
                            defaults={
                                'product_name': item.product_name,
                                'price_at_time': item.price_at_time,
                                'selected_attributes': item.selected_attributes,
                            }
                        )
                        if not created:
                            cart_item.quantity += item.quantity
                            cart_item.save()

                    # Đánh dấu session cart là đã merge
                    session_cart.status = 'merged'
                    session_cart.save()
                else:
                    # Nếu user chưa có cart, gán session cart cho user
                    session_cart.user_id = request.user.id
                    session_cart.save()
                    cart = session_cart

                # Xóa session_id
                del request.session['cart_session_id']

        # Nếu vẫn chưa có cart, tạo mới
        if not cart:
            cart = Cart.objects.create(user_id=request.user.id)
    else:
        # Xử lý cho khách không đăng nhập
        session_id = request.session.get('cart_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session['cart_session_id'] = session_id

        cart = Cart.objects.filter(session_id=session_id, status='active').first()
        if not cart:
            cart = Cart.objects.create(session_id=session_id)

    return cart


def view_cart(request):
    """Xem giỏ hàng"""
    cart = _get_or_create_cart(request)
    cart_items = cart.items.all()

    # Tính tổng tiền
    subtotal = sum(item.quantity * item.price_at_time for item in cart_items)

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
    }
    return render(request, 'order_service/cart.html', context)


@require_POST
def add_to_cart(request, product_id):
    """Thêm sản phẩm vào giỏ hàng"""
    cart = _get_or_create_cart(request)

    # Lấy thông tin sản phẩm từ Product Service
    # TODO: Thay thế bằng API call thực tế đến Product Service
    product_data = {
        'id': product_id,
        'name': request.POST.get('product_name'),
        'price': float(request.POST.get('price', 0)),
    }

    quantity = int(request.POST.get('quantity', 1))
    selected_attributes = json.loads(request.POST.get('attributes', '{}'))

    # Kiểm tra nếu sản phẩm đã có trong giỏ hàng với cùng thuộc tính
    cart_item = CartItem.objects.filter(
        cart=cart,
        product_id=product_id,
        selected_attributes=selected_attributes
    ).first()

    if cart_item:
        cart_item.quantity += quantity
        cart_item.save()
    else:
        CartItem.objects.create(
            cart=cart,
            product_id=product_id,
            product_name=product_data['name'],
            quantity=quantity,
            price_at_time=product_data['price'],
            selected_attributes=selected_attributes,
        )

    messages.success(request, "Đã thêm sản phẩm vào giỏ hàng!")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('order_service:view_cart')


@require_POST
def update_cart_item(request, item_id):
    """Cập nhật số lượng sản phẩm trong giỏ hàng"""
    cart = _get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()

    messages.success(request, "Đã cập nhật giỏ hàng!")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('order_service:view_cart')


@require_POST
def remove_from_cart(request, item_id):
    """Xóa sản phẩm khỏi giỏ hàng"""
    cart = _get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()

    messages.success(request, "Đã xóa sản phẩm khỏi giỏ hàng!")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('order_service:view_cart')


@require_POST
def clear_cart(request):
    """Xóa tất cả sản phẩm trong giỏ hàng"""
    cart = _get_or_create_cart(request)
    cart.items.all().delete()

    messages.success(request, "Đã xóa tất cả sản phẩm trong giỏ hàng!")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('order_service:view_cart')


@login_required
def checkout(request):
    """Trang checkout bước 1: Xác nhận giỏ hàng"""
    cart = _get_or_create_cart(request)
    cart_items = cart.items.all()

    if not cart_items:
        messages.warning(request, "Giỏ hàng của bạn đang trống!")
        return redirect('order_service:view_cart')

    # Tính tổng tiền
    subtotal = sum(item.quantity * item.price_at_time for item in cart_items)

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
    }
    return render(request, 'order_service/checkout.html', context)


@login_required
def checkout_shipping(request):
    """Trang checkout bước 2: Chọn địa chỉ và phương thức vận chuyển"""
    cart = _get_or_create_cart(request)

    # Lấy danh sách địa chỉ từ User Service
    # TODO: Thay thế bằng API call thực tế đến User Service
    addresses = []  # Giả định dữ liệu địa chỉ

    # Lấy danh sách phương thức vận chuyển từ Shipping Service
    # TODO: Thay thế bằng API call thực tế đến Shipping Service
    shipping_methods = []  # Giả định dữ liệu shipping

    context = {
        'addresses': addresses,
        'shipping_methods': shipping_methods,
    }
    return render(request, 'order_service/checkout_shipping.html', context)


@login_required
def checkout_payment(request):
    """Trang checkout bước 3: Chọn phương thức thanh toán"""
    if request.method == 'POST':
        # Lưu thông tin địa chỉ và phương thức vận chuyển vào session
        request.session['shipping_address_id'] = request.POST.get('shipping_address_id')
        request.session['shipping_method'] = request.POST.get('shipping_method')

    # Lấy danh sách phương thức thanh toán từ Payment Service
    # TODO: Thay thế bằng API call thực tế đến Payment Service
    payment_methods = []  # Giả định dữ liệu payment

    context = {
        'payment_methods': payment_methods,
    }
    return render(request, 'order_service/checkout_payment.html', context)


@login_required
def checkout_complete(request):
    """Hoàn tất đơn hàng"""
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        cart = _get_or_create_cart(request)
        cart_items = cart.items.all()

        if not cart_items:
            messages.warning(request, "Giỏ hàng của bạn đang trống!")
            return redirect('order_service:view_cart')

        shipping_address_id = request.session.get('shipping_address_id')
        shipping_method = request.session.get('shipping_method')

        # Lấy thông tin địa chỉ từ User Service
        # TODO: Thay thế bằng API call thực tế đến User Service
        shipping_address_data = {}  # Giả định dữ liệu địa chỉ

        # Tính toán chi phí
        subtotal = sum(item.quantity * item.price_at_time for item in cart_items)
        shipping_cost = 0  # Tính chi phí vận chuyển thực tế
        tax = subtotal * 0.1  # Giả định VAT 10%
        total_amount = subtotal + shipping_cost + tax

        try:
            with transaction.atomic():
                # Tạo đơn hàng mới
                order = Order.objects.create(
                    user_id=request.user.id,
                    email=request.user.email,
                    shipping_address_id=shipping_address_id,
                    shipping_address_data=shipping_address_data,
                    billing_address_data=shipping_address_data,  # Sử dụng cùng địa chỉ cho billing
                    status='pending',
                    payment_status='pending',
                    shipping_method=shipping_method,
                    shipping_cost=shipping_cost,
                    subtotal=subtotal,
                    tax=tax,
                    discount=0,
                    total_amount=total_amount,
                )

                # Tạo các order items
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product_id=item.product_id,
                        product_name=item.product_name,
                        quantity=item.quantity,
                        price_at_time=item.price_at_time,
                        selected_attributes=item.selected_attributes,
                        vendor_id=0,  # Lấy thông tin vendor từ product
                        subtotal=item.quantity * item.price_at_time,
                    )

                # Tạo lịch sử trạng thái
                OrderStatusHistory.objects.create(
                    order=order,
                    status='pending',
                    notes='Đơn hàng mới được tạo',
                    created_by=request.user.id,
                )

                # Gửi thông tin thanh toán đến Payment Service
                # TODO: Thay thế bằng API call thực tế đến Payment Service

                # Đánh dấu giỏ hàng là đã chuyển thành đơn hàng
                cart.status = 'converted'
                cart.save()

                # Xóa session liên quan đến checkout
                if 'shipping_address_id' in request.session:
                    del request.session['shipping_address_id']
                if 'shipping_method' in request.session:
                    del request.session['shipping_method']

                messages.success(request, f"Đơn hàng #{order.order_number} đã được tạo thành công!")
                return redirect('order_service:order_detail', pk=order.id)

        except Exception as e:
            messages.error(request, f"Có lỗi xảy ra khi tạo đơn hàng: {str(e)}")
            return redirect('order_service:checkout')

    # Nếu không phải POST, chuyển về bước 1
    return redirect('order_service:checkout')


@login_required
def order_list(request):
    """Danh sách đơn hàng của người dùng"""
    orders = Order.objects.filter(user_id=request.user.id).order_by('-created_at')

    # Lọc theo trạng thái
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)

    # Phân trang
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status,
    }
    return render(request, 'order_service/order_list.html', context)


@login_required
def order_detail(request, pk):
    """Chi tiết đơn hàng"""
    order = get_object_or_404(Order, pk=pk, user_id=request.user.id)
    order_items = order.items.all()
    status_history = order.status_history.all().order_by('-created_at')

    context = {
        'order': order,
        'order_items': order_items,
        'status_history': status_history,
    }
    return render(request, 'order_service/order_detail.html', context)


@login_required
def cancel_order(request, pk):
    """Hủy đơn hàng"""
    order = get_object_or_404(Order, pk=pk, user_id=request.user.id)

    # Kiểm tra xem đơn hàng có thể hủy không
    if order.status not in ['pending', 'processing']:
        messages.error(request, "Không thể hủy đơn hàng trong trạng thái này!")
        return redirect('order_service:order_detail', pk=order.id)

    if request.method == 'POST':
        reason = request.POST.get('reason', 'Lý do không xác định')

        try:
            with transaction.atomic():
                # Cập nhật trạng thái đơn hàng
                order.status = 'cancelled'
                order.save()

                # Tạo lịch sử trạng thái
                OrderStatusHistory.objects.create(
                    order=order,
                    status='cancelled',
                    notes=f"Đơn hàng bị hủy bởi người dùng. Lý do: {reason}",
                    created_by=request.user.id,
                )

                # TODO: Xử lý hoàn tiền nếu cần thiết

                messages.success(request, "Đơn hàng đã được hủy thành công!")
                return redirect('order_service:order_detail', pk=order.id)

        except Exception as e:
            messages.error(request, f"Có lỗi xảy ra khi hủy đơn hàng: {str(e)}")

    return render(request, 'order_service/cancel_order.html', {'order': order})


@login_required
def view_wishlist(request):
    """Xem danh sách yêu thích"""
    wishlist, created = Wishlist.objects.get_or_create(user_id=request.user.id)
    wishlist_items = wishlist.items.all()

    # Lấy thông tin chi tiết sản phẩm từ Product Service
    # TODO: Thay thế bằng API call thực tế đến Product Service

    context = {
        'wishlist': wishlist,
        'wishlist_items': wishlist_items,
    }
    return render(request, 'order_service/wishlist.html', context)


@login_required
@require_POST
def add_to_wishlist(request, product_id):
    """Thêm sản phẩm vào danh sách yêu thích"""
    wishlist, created = Wishlist.objects.get_or_create(user_id=request.user.id)

    # Kiểm tra xem sản phẩm đã có trong wishlist chưa
    item_exists = WishlistItem.objects.filter(wishlist=wishlist, product_id=product_id).exists()

    if not item_exists:
        WishlistItem.objects.create(wishlist=wishlist, product_id=product_id)
        messages.success(request, "Đã thêm sản phẩm vào danh sách yêu thích!")
    else:
        messages.info(request, "Sản phẩm đã có trong danh sách yêu thích!")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('order_service:view_wishlist')


@login_required
@require_POST
def remove_from_wishlist(request, item_id):
    """Xóa sản phẩm khỏi danh sách yêu thích"""
    wishlist = Wishlist.objects.get(user_id=request.user.id)
    item = get_object_or_404(WishlistItem, id=item_id, wishlist=wishlist)
    item.delete()

    messages.success(request, "Đã xóa sản phẩm khỏi danh sách yêu thích!")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('order_service:view_wishlist')


@login_required
@require_POST
def move_to_cart(request, item_id):
    """Chuyển sản phẩm từ wishlist sang giỏ hàng"""
    wishlist = Wishlist.objects.get(user_id=request.user.id)
    wishlist_item = get_object_or_404(WishlistItem, id=item_id, wishlist=wishlist)

    # Lấy thông tin sản phẩm từ Product Service
    # TODO: Thay thế bằng API call thực tế đến Product Service
    product_data = {
        'id': wishlist_item.product_id,
        'name': f"Product {wishlist_item.product_id}",
        'price': 0,  # Giá sẽ được lấy từ API
    }

    # Thêm vào giỏ hàng
    cart = _get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product_id=wishlist_item.product_id,
        defaults={
            'product_name': product_data['name'],
            'price_at_time': product_data['price'],
            'quantity': 1,
        }
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # Xóa khỏi wishlist nếu được yêu cầu
    if request.POST.get('remove_from_wishlist') == 'true':
        wishlist_item.delete()

    messages.success(request, "Đã thêm sản phẩm vào giỏ hàng!")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('order_service:view_cart')


@login_required
def vendor_orders(request):
    """Danh sách đơn hàng của người bán"""
    # Lấy thông tin vendor_id
    vendor_id = request.user.id

    # Lấy các đơn hàng có sản phẩm của vendor
    order_items = OrderItem.objects.filter(vendor_id=vendor_id).values('order_id').distinct()
    order_ids = [item['order_id'] for item in order_items]
    orders = Order.objects.filter(id__in=order_ids).order_by('-created_at')

    # Lọc theo trạng thái
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)

    # Phân trang
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status,
    }
    return render(request, 'order_service/vendor/orders.html', context)


@login_required
def vendor_order_detail(request, pk):
    """Chi tiết đơn hàng của vendor"""
    # Lấy thông tin vendor_id
    vendor_id = request.user.id

    # Kiểm tra quyền truy cập
    if not OrderItem.objects.filter(order_id=pk, vendor_id=vendor_id).exists():
        messages.error(request, "Bạn không có quyền xem đơn hàng này!")
        return redirect('order_service:vendor_orders')

    order = get_object_or_404(Order, pk=pk)
    # Chỉ lấy các order items của vendor
    order_items = order.items.filter(vendor_id=vendor_id)
    status_history = order.status_history.all().order_by('-created_at')

    context = {
        'order': order,
        'order_items': order_items,
        'status_history': status_history,
    }
    return render(request, 'order_service/vendor/order_detail.html', context)


@login_required
@require_POST
def update_order_status(request, pk):
    """Cập nhật trạng thái đơn hàng bởi vendor"""
    # Lấy thông tin vendor_id
    vendor_id = request.user.id

    # Kiểm tra quyền truy cập
    if not OrderItem.objects.filter(order_id=pk, vendor_id=vendor_id).exists():
        messages.error(request, "Bạn không có quyền cập nhật đơn hàng này!")
        return redirect('order_service:vendor_orders')

    order = get_object_or_404(Order, pk=pk)
    new_status = request.POST.get('status')
    notes = request.POST.get('notes', '')

    # Kiểm tra tính hợp lệ của trạng thái mới
    if new_status not in [s[0] for s in Order.STATUS_CHOICES]:
        messages.error(request, "Trạng thái không hợp lệ!")
        return redirect('order_service:vendor_order_detail', pk=order.id)

    # Kiểm tra logic chuyển trạng thái
    if (order.status == 'cancelled' or order.status == 'refunded'):
        messages.error(request, "Không thể thay đổi trạng thái của đơn hàng đã hủy hoặc hoàn tiền!")
        return redirect('order_service:vendor_order_detail', pk=order.id)

    try:
        with transaction.atomic():
            # Cập nhật trạng thái
            order.status = new_status
            order.save()

            # Tạo lịch sử trạng thái
            OrderStatusHistory.objects.create(
                order=order,
                status=new_status,
                notes=notes,
                created_by=request.user.id,
            )

            messages.success(request, "Đã cập nhật trạng thái đơn hàng!")
    except Exception as e:
        messages.error(request, f"Có lỗi xảy ra: {str(e)}")

    return redirect('order_service:vendor_order_detail', pk=order.id)


@api_view(['GET'])
def cart_item_count(request):
    """API endpoint để lấy số lượng sản phẩm trong giỏ hàng"""
    cart = _get_or_create_cart(request)
    count = cart.items.aggregate(total=Sum('quantity'))['total'] or 0
    return Response({'count': count})


@api_view(['GET'])
def get_order_status(request, order_id):
    """API endpoint để lấy trạng thái đơn hàng"""
    try:
        if request.user.is_authenticated:
            order = Order.objects.get(id=order_id, user_id=request.user.id)
        else:
            return Response({'error': 'Unauthorized'}, status=401)

        return Response({
            'status': order.status,
            'payment_status': order.payment_status,
            'updated_at': order.updated_at,
        })
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)