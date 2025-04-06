from django.urls import path
from . import views

app_name = 'analytic_service'

urlpatterns = [
    # User Analytics
    path('log-activity/', views.log_user_activity, name='log_user_activity'),
    path('user-behavior/', views.user_behavior, name='user_behavior'),

    # Product Analytics
    path('product-performance/', views.product_performance, name='product_performance'),
    path('product-views/<int:product_id>/', views.increment_product_views, name='increment_product_views'),

    # Sales Analytics
    path('sales/', views.sales_analytics, name='sales_analytics'),
    path('sales/by-period/', views.sales_by_period, name='sales_by_period'),
    path('sales/by-category/', views.sales_by_category, name='sales_by_category'),

    # Dashboards
    path('dashboard/vendor/', views.vendor_dashboard, name='vendor_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),

    # Reports
    path('reports/generate/', views.generate_report, name='generate_report'),
    path('reports/scheduled/', views.scheduled_reports, name='scheduled_reports'),

    # Search Analytics
    path('search-trends/', views.search_trends, name='search_trends'),
    path('popular-searches/', views.popular_searches, name='popular_searches'),

    # Analytics API
    path('api/real-time-stats/', views.real_time_stats, name='real_time_stats'),
    path('api/conversion-rate/', views.conversion_rate, name='conversion_rate'),
]