from django.urls import path
from . import views

app_name = 'recommendation_service'

urlpatterns = [
    # Reviews and Ratings
    path('products/<int:product_id>/reviews/', views.product_reviews, name='product_reviews'),
    path('products/<int:product_id>/reviews/add/', views.add_review, name='add_review'),
    path('reviews/<int:pk>/update/', views.update_review, name='update_review'),
    path('reviews/<int:pk>/delete/', views.delete_review, name='delete_review'),

    # User Reviews
    path('my-reviews/', views.user_reviews, name='user_reviews'),

    # Recommendations
    path('recommended/', views.recommended_products, name='recommended_products'),
    path('similar/<int:product_id>/', views.similar_products, name='similar_products'),
    path('frequently-bought-together/<int:product_id>/', views.frequently_bought_together,
         name='frequently_bought_together'),
    path('based-on-history/', views.based_on_history, name='based_on_history'),

    # Vendor Review Management
    path('vendor/reviews/', views.vendor_reviews, name='vendor_reviews'),
    path('vendor/reviews/<int:pk>/respond/', views.respond_to_review, name='respond_to_review'),

    # User Preferences
    path('preferences/', views.user_preferences, name='user_preferences'),
    path('preferences/update/', views.update_preferences, name='update_preferences'),

    # Recommendation API
    path('api/top-rated/', views.top_rated_products, name='top_rated_products'),
    path('api/sentiment-analysis/<int:product_id>/', views.sentiment_analysis, name='sentiment_analysis'),
]