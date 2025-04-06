# apps/payment_service/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
import uuid
import requests
from .models import PaymentMethod, Payment, Transaction, Refund, VendorPayment
from .serializers import PaymentMethodSerializer, PaymentSerializer, RefundSerializer
from .forms import PaymentMethodForm, RefundRequestForm


@login_required
def payment_methods(request):
    """Hiển thị danh sách phương thức thanh toán của người dùng"""
    payment_methods = PaymentMethod.objects.filter(user_id=request.user.id)
    return render(request, 'payment_service/payment_methods.html', {'payment_methods': payment_methods})


@login_required
def add_payment_method(request):
    """Thêm phương thức thanh toán mới"""
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            payment_method = form.save(commit=False)
            payment_method.user_id = request.user.id

            # Mã hóa thông tin nhạy cảm
            # TODO: Thêm mã hóa thông tin thẻ

            payment_method.save()
            messages.success(request, "Đã thêm phương thức thanh toán mới!")
            return redirect('payment_service:payment_methods')
        else:
            messages.error(request, "Thêm phương thức thanh toán không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = PaymentMethodForm()

    return render(request, 'payment_service/add_payment_method.html', {'form': form})


@login_required
def update_payment_method(request, pk):
    """Cập nhật phương thức thanh toán"""
    payment_method = get_object_or_404(PaymentMethod, pk=pk, user_id=request.user.id)

    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, instance=payment_method)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã cập nhật phương thức thanh toán!")
            return redirect('payment_service:payment_methods')
        else:
            messages.error(request, "Cập nhật không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = PaymentMethodForm(instance=payment_method)

    return render(request, 'payment_service/update_payment_method.html',
                  {'form': form, 'payment_method': payment_method})


@login_required
def delete_payment_method(request, pk):
    """Xóa phương thức thanh toán"""
    payment_method = get_object_or_404(PaymentMethod, pk=pk, user_id=request.user.id)

    if request.method == 'POST':
        payment_method.delete()
        messages.success(request, "Đã xóa phương thức thanh toán!")
        return redirect('payment_service:payment_methods')

    return render(request, 'payment_service/delete_payment_method.html', {'payment_method': payment_method})


@login_required
def set_default_payment_method(request, pk):
    """Đặt phương thức thanh toán mặc định"""
    payment_method = get_object_or_404(PaymentMethod, pk=pk, user_id=request.user.id)

    # Đặt tất cả các phương thức khác về non-default
    PaymentMethod.objects.filter(user_id=request.user.id).update(is_default=False)

    # Đặt phương thức này thành mặc định
    payment_method.is_default = True
    payment_method.save()

    messages.success(request, "Đã đặt phương thức thanh toán mặc định mới!")
    return redirect('payment_service:payment_methods')


@login_required
def process_payment(request, order_id):
    """Xử lý thanh toán cho đơn hàng"""
    # Lấy thông tin đơn hàng từ Order Service
    # TODO: Thay thế bằng API call thực tế đến Order Service
    order_data = {
        'id': order_id,
        'total_amount': 1000000,
        'status': 'pending'
    }

    if request.method == 'POST':
        payment_method_id = request.POST.get('payment_method_id')
        payment_method = None

        if payment_method_id:
            payment_method = get_object_or_404(PaymentMethod, pk=payment_method_id, user_id=request.user.id)

        gateway = request.POST.get('payment_gateway', 'direct')

        try:
            with transaction.atomic():
                # Tạo payment record
                payment = Payment.objects.create(
                    order_id=order_id,
                    user_id=request.user.id,
                    payment_method=payment_method.payment_type if payment_method else 'unknown',
                    amount=order_data['total_amount'],
                    currency='VND',
                    gateway=gateway,
                    status='pending'
                )

                # Tích hợp với cổng thanh toán
                if gateway == 'direct':
                    # Xử lý thanh toán trực tiếp
                    transaction = Transaction.objects.create(
                        payment=payment,
                        amount=payment.amount,
                        transaction_type='charge',
                        status='completed',
                        gateway_response={'success': True}
                    )

                    payment.status = 'completed'
                    payment.save()

                    # Cập nhật trạng thái đơn hàng
                    # TODO: Gửi request đến Order Service để cập nhật trạng thái

                    messages.success(request, "Thanh toán thành công!")
                    return redirect('payment_service:payment_success')

                elif gateway in ['vnpay', 'momo', 'zalopay']:
                    # Chuyển hướng đến cổng thanh toán bên thứ ba
                    # TODO: Tích hợp với các cổng thanh toán thực tế
                    return redirect('payment_service:payment_callback', gateway=gateway)
                else:
                    messages.error(request, "Cổng thanh toán không được hỗ trợ!")
                    return redirect('order_service:checkout_payment')

        except Exception as e:
            messages.error(request, f"Có lỗi xảy ra khi xử lý thanh toán: {str(e)}")
            return redirect('order_service:checkout_payment')

    # Lấy các phương thức thanh toán của người dùng
    payment_methods = PaymentMethod.objects.filter(user_id=request.user.id)
    context = {
        'order_id': order_id,
        'order_data': order_data,
        'payment_methods': payment_methods,
    }
    return render(request, 'payment_service/process_payment.html', context)


@csrf_exempt
def payment_callback(request, gateway):
    """Callback từ cổng thanh toán"""
    if request.method == 'POST':
        # Xử lý callback từ cổng thanh toán
        # TODO: Thêm logic xử lý callback thực tế
        data = json.loads(request.body)

        payment_id = data.get('payment_id')
        transaction_id = data.get('transaction_id')
        status = data.get('status')

        try:
            payment = Payment.objects.get(id=payment_id)

            # Tạo transaction record
            Transaction.objects.create(
                payment=payment,
                amount=payment.amount,
                transaction_type='charge',
                status=status,
                gateway_response=data
            )

            # Cập nhật trạng thái payment
            payment.status = status
            payment.gateway_payment_id = transaction_id
            payment.save()

            # Cập nhật trạng thái đơn hàng
            # TODO: Gửi request đến Order Service để cập nhật trạng thái

            return JsonResponse({'success': True})

        except Payment.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Payment not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return redirect('payment_service:payment_success')


def payment_success(request):
    """Trang thanh toán thành công"""
    return render(request, 'payment_service/payment_success.html')


def payment_failed(request):
    """Trang thanh toán thất bại"""
    error = request.GET.get('error', 'Có lỗi xảy ra trong quá trình thanh toán.')
    return render(request, 'payment_service/payment_failed.html', {'error': error})


@login_required
def request_refund(request, order_id):
    """Yêu cầu hoàn tiền"""
    # Lấy thông tin đơn hàng từ Order Service
    # TODO: Thay thế bằng API call thực tế đến Order Service
    order_data = {
        'id': order_id,
        'total_amount': 1000000,
        'status': 'delivered'
    }

    # Kiểm tra điều kiện hoàn tiền
    if order_data['status'] not in ['delivered', 'shipped']:
        messages.error(request, "Đơn hàng không đủ điều kiện để yêu cầu hoàn tiền!")
        return redirect('order_service:order_detail', pk=order_id)

    # Tìm payment tương ứng
    try:
        payment = Payment.objects.get(order_id=order_id, user_id=request.user.id)
    except Payment.DoesNotExist:
        messages.error(request, "Không tìm thấy thông tin thanh toán cho đơn hàng này!")
        return redirect('order_service:order_detail', pk=order_id)

    if request.method == 'POST':
        form = RefundRequestForm(request.POST)
        if form.is_valid():
            refund = form.save(commit=False)
            refund.payment = payment
            refund.save()

            # Cập nhật trạng thái đơn hàng
            # TODO: Gửi request đến Order Service để cập nhật trạng thái

            messages.success(request, "Yêu cầu hoàn tiền đã được gửi và đang được xử lý!")
            return redirect('order_service:order_detail', pk=order_id)
        else:
            messages.error(request, "Yêu cầu hoàn tiền không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = RefundRequestForm(initial={'amount': payment.amount})

    context = {
        'form': form,
        'order_id': order_id,
        'payment': payment,
    }
    return render(request, 'payment_service/request_refund.html', context)


@login_required
def refund_list(request):
    """Danh sách yêu cầu hoàn tiền của người dùng"""
    payments = Payment.objects.filter(user_id=request.user.id)
    refunds = Refund.objects.filter(payment__in=payments).order_by('-created_at')

    # Lọc theo trạng thái
    status = request.GET.get('status')
    if status:
        refunds = refunds.filter(status=status)

    # Phân trang
    paginator = Paginator(refunds, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status,
    }
    return render(request, 'payment_service/refund_list.html', context)


@login_required
def refund_detail(request, pk):
    """Chi tiết yêu cầu hoàn tiền"""
    payments = Payment.objects.filter(user_id=request.user.id)
    refund = get_object_or_404(Refund, pk=pk, payment__in=payments)

    context = {
        'refund': refund,
    }
    return render(request, 'payment_service/refund_detail.html', context)


@login_required
def vendor_transactions(request):
    """Danh sách giao dịch của người bán"""
    # Lấy thông tin vendor_id
    vendor_id = request.user.id

    # Lấy danh sách giao dịch
    vendor_payments = VendorPayment.objects.filter(vendor_id=vendor_id).order_by('-created_at')

    # Lọc theo trạng thái
    status = request.GET.get('status')
    if status:
        vendor_payments = vendor_payments.filter(status=status)

    # Phân trang
    paginator = Paginator(vendor_payments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status,
    }
    return render(request, 'payment_service/vendor/transactions.html', context)


@login_required
def vendor_earnings(request):
    """Thống kê doanh thu của người bán"""
    # Lấy thông tin vendor_id
    vendor_id = request.user.id

    # TODO: Tính toán doanh thu và thống kê
    earnings_data = {}

    context = {
        'earnings_data': earnings_data,
    }
    return render(request, 'payment_service/vendor/earnings.html', context)


@login_required
def vendor_withdraw(request):
    """Yêu cầu rút tiền của người bán"""
    # Lấy thông tin vendor_id
    vendor_id = request.user.id

    # TODO: Xử lý yêu cầu rút tiền

    if request.method == 'POST':
        amount = float(request.POST.get('amount', 0))
        payment_method = request.POST.get('payment_method')

        # Kiểm tra điều kiện rút tiền
        # TODO: Thêm logic kiểm tra số dư

        try:
            # Tạo yêu cầu rút tiền
            VendorPayment.objects.create(
                vendor_id=vendor_id,
                amount=amount,
                description=f"Rút tiền qua {payment_method}",
                status='pending',
                payment_method=payment_method,
            )
            messages.success(request, "Yêu cầu rút tiền đã được gửi và đang được xử lý!")
            return redirect('payment_service:vendor_transactions')
        except Exception as e:
            messages.error(request, f"Có lỗi xảy ra: {str(e)}")

    return render(request, 'payment_service/vendor/withdraw.html')


@api_view(['GET'])
def available_payment_gateways(request):
    """API endpoint để lấy danh sách cổng thanh toán khả dụng"""
    gateways = [
        {'id': 'direct', 'name': 'Thanh toán trực tiếp'},
        {'id': 'vnpay', 'name': 'VNPay'},
        {'id': 'momo', 'name': 'MoMo'},
        {'id': 'zalopay', 'name': 'ZaloPay'},
    ]
    return Response(gateways)


@api_view(['GET'])
def transaction_status(request, transaction_id):
    """API endpoint để kiểm tra trạng thái giao dịch"""
    try:
        transaction = Transaction.objects.get(transaction_id=transaction_id)
        return Response({
            'status': transaction.status,
            'transaction_type': transaction.transaction_type,
            'created_at': transaction.created_at,
        })
    except Transaction.DoesNotExist:
        return Response({'error': 'Transaction not found'}, status=404)