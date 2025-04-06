# apps/recommendation_service/models.py
from django.db import models
from djongo.models import DjongoManager


class Review(models.Model):
    """Đánh giá sản phẩm"""
    product_id = models.IntegerField()  # Foreign key to Product in Product Service
    user_id = models.IntegerField()  # Foreign key to User in User Service
    rating = models.IntegerField()  # 1-5 stars
    title = models.CharField(max_length=255, blank=True)
    comment = models.TextField(blank=True)
    verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    helpful_votes = models.IntegerField(default=0)

    objects = DjongoManager()

    def __str__(self):
        return f"Review for Product {self.product_id} by User {self.user_id}"

    class Meta:
        db_table = 'reviews'
        unique_together = ('product_id', 'user_id')
        indexes = [
            models.Index(fields=['product_id']),
            models.Index(fields=['user_id']),
            models.Index(fields=['created_at']),
        ]


class ReviewImage(models.Model):
    """Hình ảnh đính kèm đánh giá sản phẩm"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image_url = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = DjongoManager()

    def __str__(self):
        return f"Image for Review {self.review.id}"

    class Meta:
        db_table = 'review_images'


class ReviewResponse(models.Model):
    """Phản hồi của người bán với đánh giá"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='responses')
    vendor_id = models.IntegerField()  # Foreign key to Vendor in User Service
    response_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = DjongoManager()

    def __str__(self):
        return f"Vendor {self.vendor_id} response to Review {self.review.id}"

    class Meta:
        db_table = 'review_responses'


class UserPreference(models.Model):
    """Sở thích người dùng"""
    user_id = models.IntegerField(unique=True)  # Foreign key to User in User Service
    favorite_categories = models.JSONField(default=list)  # List of category IDs
    preferred_price_range = models.JSONField(default=dict)  # Min and max price
    disliked_products = models.JSONField(default=list)  # List of product IDs
    last_updated = models.DateTimeField(auto_now=True)

    objects = DjongoManager()

    def __str__(self):
        return f"Preferences for User {self.user_id}"

    class Meta:
        db_table = 'user_preferences'


class ProductSentiment(models.Model):
    """Phân tích cảm xúc của sản phẩm từ các đánh giá"""
    product_id = models.IntegerField(unique=True)  # Foreign key to Product in Product Service
    overall_sentiment = models.FloatField()  # -1 to 1 (negative to positive)
    sentiment_distribution = models.JSONField()  # Distribution of sentiments
    key_positive_aspects = models.JSONField(default=list)  # Positive points mentioned in reviews
    key_negative_aspects = models.JSONField(default=list)  # Negative points mentioned in reviews
    last_updated = models.DateTimeField(auto_now=True)

    objects = DjongoManager()

    def __str__(self):
        return f"Sentiment for Product {self.product_id}"

    class Meta:
        db_table = 'product_sentiments'


class RecommendationLog(models.Model):
    """Ghi nhận các đề xuất đã hiển thị cho người dùng"""
    user_id = models.IntegerField()  # Foreign key to User in User Service
    product_id = models.IntegerField()  # Foreign key to Product in Product Service
    action_type = models.CharField(max_length=50)  # e.g., 'view', 'click', 'purchase', 'ignore'
    recommendation_type = models.CharField(max_length=50)  # e.g., 'similar_products', 'frequently_bought_together'
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = DjongoManager()

    def __str__(self):
        return f"Recommendation for User {self.user_id} - Product {self.product_id}"

    class Meta:
        db_table = 'recommendation_logs'
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['product_id']),
            models.Index(fields=['timestamp']),
        ]