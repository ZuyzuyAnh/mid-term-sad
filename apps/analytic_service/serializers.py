# apps/analytic_service/serializers.py
from rest_framework import serializers
from .models import (
    UserActivity, SellerAnalytics, ProductPerformance,
    SearchQuery, AggregatedStatistics
)

class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user_id', 'session_id', 'ip_address', 'activity_type',
            'page', 'product_id', 'category_id', 'device_info', 'referrer',
            'timestamp'
        ]

# apps/analytic_service/serializers.py (tiếp)
class SellerAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerAnalytics
        fields = [
            'id', 'seller_id', 'period', 'period_start', 'period_end',
            'total_sales', 'total_revenue', 'average_order_value',
            'product_performance', 'average_rating', 'generated_at'
        ]

class ProductPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPerformance
        fields = [
            'id', 'product_id', 'period', 'period_start', 'period_end',
            'views', 'unique_views', 'cart_adds', 'purchases', 'revenue',
            'conversion_rate', 'average_rating', 'generated_at'
        ]

class SearchQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchQuery
        fields = [
            'id', 'query_text', 'user_id', 'session_id', 'results_count',
            'filters_applied', 'clicked_products', 'timestamp'
        ]

class AggregatedStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AggregatedStatistics
        fields = [
            'id', 'metric_name', 'period', 'period_start', 'period_end',
            'value', 'additional_data', 'generated_at'
        ]