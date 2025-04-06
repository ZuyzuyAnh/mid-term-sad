# apps/recommendation_service/serializers.py
from rest_framework import serializers
from .models import (
    Review, ReviewImage, ReviewResponse, UserPreference,
    ProductSentiment, RecommendationLog
)


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ['id', 'image_url', 'created_at']


class ReviewResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewResponse
        fields = ['id', 'vendor_id', 'response_text', 'created_at', 'updated_at']


class ReviewSerializer(serializers.ModelSerializer):
    images = ReviewImageSerializer(many=True, read_only=True)
    responses = ReviewResponseSerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'product_id', 'user_id', 'rating', 'title', 'comment',
            'verified_purchase', 'created_at', 'updated_at', 'helpful_votes',
            'images', 'responses'
        ]


class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = [
            'id', 'user_id', 'favorite_categories', 'preferred_price_range',
            'disliked_products', 'last_updated'
        ]


class ProductSentimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSentiment
        fields = [
            'id', 'product_id', 'overall_sentiment', 'sentiment_distribution',
            'key_positive_aspects', 'key_negative_aspects', 'last_updated'
        ]


class RecommendationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendationLog
        fields = [
            'id', 'user_id', 'product_id', 'action_type',
            'recommendation_type', 'timestamp'
        ]