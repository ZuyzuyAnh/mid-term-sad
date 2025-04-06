# apps/analytic_service/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Sum, Avg, F, Q
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
from datetime import datetime, timedelta
from djongo.models import DjongoManager
from .models import (
    UserActivity, SellerAnalytics, ProductPerformance,
    SearchQuery, AggregatedStatistics
)
from .serializers import UserActivitySerializer, ProductPerformanceSerializer
from .forms import ReportForm


@csrf_exempt
def log_user_activity(request):
    """Ghi nhận hoạt động người dùng"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = request.user.id if request.user.is_authenticated else None

            UserActivity.objects.create(
                user_id=user_id,
                session_id=request.session.session_key,
                ip_address=request.META.get('REMOTE_ADDR'),
                activity_type=data.get('activity_type'),
                page=data.get('page'),
                product_id=data.get('product_id'),
                category_id=data.get('category_id'),
                device_info=data.get('device_info', {}),
                referrer=data.get('referrer', ''),
            )

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@login_required
def user_behavior(request):
    """Phân tích hành vi người dùng"""
    if not request.user.is_staff:
        return redirect('home')

    # Lấy dữ liệu hoạt động gần đây
    recent_activities = UserActivity.objects.all().order_by('-timestamp')[:100]

    # Thống kê theo loại hoạt động
    activity_stats = UserActivity.objects.values('activity_type').annotate(
        count=Count('id')
    ).order_by('-count')

    # Thống kê theo trang
    page_stats = UserActivity.objects.values('page').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    context = {
        'recent_activities': recent_activities,
        'activity_stats': activity_stats,
        'page_stats': page_stats,
    }
    return render(request, 'analytic_service/user_behavior.html', context)


@login_required
def product_performance(request):
    """Phân tích hiệu suất sản phẩm"""
    # Chỉ vendor và admin có thể xem
    vendor_id = request.user.id

    # Lọc theo period
    period = request.GET.get('period', 'monthly')
    start_date = None

    now = timezone.now().date()
    if period == 'daily':
        start_date = now - timedelta(days=30)
    elif period == 'weekly':
        start_date = now - timedelta(weeks=12)
    elif period == 'monthly':
        start_date = now - timedelta(days=365)
    elif period == 'yearly':
        start_date = now - timedelta(days=365 * 3)

    # Lấy dữ liệu hiệu suất sản phẩm
    if request.user.is_staff:
        # Admin xem tất cả sản phẩm
        performances = ProductPerformance.objects.filter(
            period=period,
            period_start__gte=start_date
        ).order_by('product_id', 'period_start')
    else:
        # Vendor chỉ xem sản phẩm của mình
        # TODO: Lấy danh sách sản phẩm của vendor
        product_ids = []
        performances = ProductPerformance.objects.filter(
            product_id__in=product_ids,
            period=period,
            period_start__gte=start_date
        ).order_by('product_id', 'period_start')

    # Lấy top sản phẩm
    top_products_views = performances.values('product_id').annotate(
        total_views=Sum('views')
    ).order_by('-total_views')[:10]

    top_products_revenue = performances.values('product_id').annotate(
        total_revenue=Sum('revenue')
    ).order_by('-total_revenue')[:10]

    top_products_conversion = performances.values('product_id').annotate(
        avg_conversion=Avg('conversion_rate')
    ).order_by('-avg_conversion')[:10]

    context = {
        'performances': performances,
        'top_products_views': top_products_views,
        'top_products_revenue': top_products_revenue,
        'top_products_conversion': top_products_conversion,
        'period': period,
    }
    return render(request, 'analytic_service/product_performance.html', context)


@require_POST
def increment_product_views(request, product_id):
    """Tăng số lượt xem sản phẩm"""
    try:
        # Tìm hoặc tạo record hiệu suất cho ngày hiện tại
        today = timezone.now().date()
        performance, created = ProductPerformance.objects.get_or_create(
            product_id=product_id,
            period='daily',
            period_start=today,
            period_end=today,
            defaults={
                'views': 0,
                'unique_views': 0,
                'cart_adds': 0,
                'purchases': 0,
                'revenue': 0,
                'conversion_rate': 0,
                'average_rating': 0,
            }
        )

        # Tăng số lượt xem
        performance.views += 1
        performance.save()

        # Kiểm tra xem là unique view không
        user_id = request.user.id if request.user.is_authenticated else None
        session_id = request.session.session_key

        today_start = datetime.combine(today, datetime.min.time())
        is_unique = not UserActivity.objects.filter(
            Q(user_id=user_id) if user_id else Q(session_id=session_id),
            product_id=product_id,
            activity_type='product_view',
            timestamp__gte=today_start
        ).exists()

        if is_unique and user_id:
            performance.unique_views += 1
            performance.save()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def sales_analytics(request):
    """Phân tích doanh số bán hàng"""
    # Chỉ vendor và admin có thể xem
    vendor_id = request.user.id

    # Lọc theo period
    period = request.GET.get('period', 'monthly')

    if request.user.is_staff:
        # Admin xem tất cả
        seller_analytics = SellerAnalytics.objects.filter(
            period=period
        ).order_by('seller_id', 'period_start')
    else:
        # Vendor chỉ xem của mình
        seller_analytics = SellerAnalytics.objects.filter(
            seller_id=vendor_id,
            period=period
        ).order_by('period_start')

    context = {
        'analytics': seller_analytics,
        'period': period,
    }
    return render(request, 'analytic_service/sales_analytics.html', context)


@login_required
def sales_by_period(request):
    """Phân tích doanh số theo thời gian"""
    # Chỉ vendor và admin có thể xem
    vendor_id = request.user.id

    # Lọc theo period
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    try:
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_date = timezone.now().date() - timedelta(days=30)

        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = timezone.now().date()
    except ValueError:
        # Xử lý lỗi định dạng ngày
        start_date = timezone.now().date() - timedelta(days=30)
        end_date = timezone.now().date()

    if request.user.is_staff:
        # Admin xem tất cả
        seller_analytics = SellerAnalytics.objects.filter(
            period_start__gte=start_date,
            period_end__lte=end_date
        ).order_by('seller_id', 'period_start')
    else:
        # Vendor chỉ xem của mình
        seller_analytics = SellerAnalytics.objects.filter(
            seller_id=vendor_id,
            period_start__gte=start_date,
            period_end__lte=end_date
        ).order_by('period_start')

    context = {
        'analytics': seller_analytics,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'analytic_service/sales_by_period.html', context)


@login_required
def sales_by_category(request):
    """Phân tích doanh số theo danh mục"""
    # Chỉ vendor và admin có thể xem
    vendor_id = request.user.id

    # TODO: Lấy dữ liệu doanh số theo danh mục
    # Cần kết hợp dữ liệu từ Order Service và Product Service

    context = {
        'categories': [],
    }
    return render(request, 'analytic_service/sales_by_category.html', context)


@login_required
def vendor_dashboard(request):
    """Bảng điều khiển thống kê cho vendor"""
    vendor_id = request.user.id

    # Lấy thống kê gần đây
    recent_stats = SellerAnalytics.objects.filter(
        seller_id=vendor_id,
        period='daily'
    ).order_by('-period_start')[:30]

    # Tính tổng doanh thu trong 30 ngày qua
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    revenue_30d = recent_stats.filter(
        period_start__gte=thirty_days_ago
    ).aggregate(total=Sum('total_revenue'))['total'] or 0

    # Tính tổng đơn hàng trong 30 ngày qua
    orders_30d = recent_stats.filter(
        period_start__gte=thirty_days_ago
    ).aggregate(total=Sum('total_sales'))['total'] or 0

    # Tính giá trị đơn hàng trung bình
    avg_order_value = recent_stats.filter(
        period_start__gte=thirty_days_ago
    ).aggregate(avg=Avg('average_order_value'))['avg'] or 0

    context = {
        'recent_stats': recent_stats,
        'revenue_30d': revenue_30d,
        'orders_30d': orders_30d,
        'avg_order_value': avg_order_value,
    }
    return render(request, 'analytic_service/vendor/dashboard.html', context)


@login_required
def admin_dashboard(request):
    """Bảng điều khiển thống kê cho admin"""
    if not request.user.is_staff:
        return redirect('home')

    # Lấy thống kê tổng hợp
    recent_stats = AggregatedStatistics.objects.filter(
        period='daily'
    ).order_by('-period_start')[:30]

    # Tính tổng doanh thu trong 30 ngày qua
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    revenue_stats = AggregatedStatistics.objects.filter(
        metric_name='total_revenue',
        period='daily',
        period_start__gte=thirty_days_ago
    ).order_by('period_start')

    # Tính tổng đơn hàng
    order_stats = AggregatedStatistics.objects.filter(
        metric_name='total_orders',
        period='daily',
        period_start__gte=thirty_days_ago
    ).order_by('period_start')

    # Tính số người dùng hoạt động
    user_stats = AggregatedStatistics.objects.filter(
        metric_name='active_users',
        period='daily',
        period_start__gte=thirty_days_ago
    ).order_by('period_start')

    context = {
        'revenue_stats': revenue_stats,
        'order_stats': order_stats,
        'user_stats': user_stats,
    }
    return render(request, 'analytic_service/admin/dashboard.html', context)


@login_required
def generate_report(request):
    """Tạo báo cáo tùy chỉnh"""
    if not request.user.is_staff and not hasattr(request.user, 'profile') or not request.user.profile.is_vendor:
        return redirect('home')

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report_type = form.cleaned_data.get('report_type')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            # TODO: Tạo báo cáo tùy chỉnh

            # Giả lập tạo báo cáo
            report_url = f"/media/reports/report_{report_type}_{start_date}_{end_date}.pdf"

            return redirect(report_url)
    else:
        form = ReportForm()

    context = {
        'form': form,
    }
    return render(request, 'analytic_service/generate_report.html', context)


@login_required
def scheduled_reports(request):
    """Quản lý báo cáo định kỳ"""
    if not request.user.is_staff and not hasattr(request.user, 'profile') or not request.user.profile.is_vendor:
        return redirect('home')

    # TODO: Quản lý báo cáo định kỳ

    context = {
        'scheduled_reports': [],
    }
    return render(request, 'analytic_service/scheduled_reports.html', context)


@login_required
def search_trends(request):
    """Phân tích xu hướng tìm kiếm"""
    if not request.user.is_staff:
        return redirect('home')

    # Lấy xu hướng tìm kiếm gần đây
    recent_searches = SearchQuery.objects.all().order_by('-timestamp')[:100]

    # Thống kê các từ khóa phổ biến
    popular_keywords = SearchQuery.objects.values('query_text').annotate(
        count=Count('id')
    ).order_by('-count')[:20]

    context = {
        'recent_searches': recent_searches,
        'popular_keywords': popular_keywords,
    }
    return render(request, 'analytic_service/search_trends.html', context)


@login_required
def popular_searches(request):
    """Hiển thị các từ khóa tìm kiếm phổ biến"""
    # Thống kê các từ khóa phổ biến
    popular_keywords = SearchQuery.objects.values('query_text').annotate(
        count=Count('id'),
        avg_results=Avg('results_count')
    ).order_by('-count')[:50]

    context = {
        'popular_keywords': popular_keywords,
    }
    return render(request, 'analytic_service/popular_searches.html', context)


@api_view(['GET'])
def real_time_stats(request):
    """API endpoint để lấy thống kê thời gian thực"""
    if not request.user.is_authenticated or (
            not request.user.is_staff and not hasattr(request.user, 'profile') or not request.user.profile.is_vendor):
        return Response({'error': 'Unauthorized'}, status=401)

    # Tính thống kê ngày hôm nay
    today = timezone.now().date()
    today_start = datetime.combine(today, datetime.min.time())

    # Số lượt xem trang
    page_views = UserActivity.objects.filter(
        timestamp__gte=today_start
    ).count()

    # Số người dùng hoạt động
    active_users = UserActivity.objects.filter(
        timestamp__gte=today_start
    ).values('user_id', 'session_id').distinct().count()

    # Số lượng đơn hàng
    # TODO: Lấy từ Order Service
    orders = 0

    # Doanh thu
    # TODO: Lấy từ Order Service
    revenue = 0

    return Response({
        'page_views': page_views,
        'active_users': active_users,
        'orders': orders,
        'revenue': revenue,
        'timestamp': timezone.now(),
    })


# apps/analytic_service/views.py (tiếp)
@api_view(['GET'])
def conversion_rate(request):
    """API endpoint để lấy tỷ lệ chuyển đổi"""
    if not request.user.is_authenticated or (
            not request.user.is_staff and not hasattr(request.user, 'profile') or not request.user.profile.is_vendor):
        return Response({'error': 'Unauthorized'}, status=401)

    # Tính tỷ lệ chuyển đổi trong 30 ngày qua
    thirty_days_ago = timezone.now().date() - timedelta(days=30)

    # Lấy các loại hoạt động
    views = UserActivity.objects.filter(
        activity_type='product_view',
        timestamp__gte=thirty_days_ago
    ).count()

    add_to_carts = UserActivity.objects.filter(
        activity_type='add_to_cart',
        timestamp__gte=thirty_days_ago
    ).count()

    purchases = UserActivity.objects.filter(
        activity_type='purchase',
        timestamp__gte=thirty_days_ago
    ).count()

    # Tính tỷ lệ
    view_to_cart = (add_to_carts / views * 100) if views > 0 else 0
    cart_to_purchase = (purchases / add_to_carts * 100) if add_to_carts > 0 else 0
    view_to_purchase = (purchases / views * 100) if views > 0 else 0

    return Response({
        'view_to_cart': round(view_to_cart, 2),
        'cart_to_purchase': round(cart_to_purchase, 2),
        'view_to_purchase': round(view_to_purchase, 2),
        'period': '30 days',
    })