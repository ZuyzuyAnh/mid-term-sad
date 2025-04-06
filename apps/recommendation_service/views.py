from django.shortcuts import render

# Create your views here.
# apps/recommendation_service/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg, Count, Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
import requests
from bson.objectid import ObjectId
from djongo.models import DjongoManager
from .models import (
    Review, ReviewImage, ReviewResponse, UserPreference,
    ProductSentiment, RecommendationLog
)
from .serializers import ReviewSerializer, ProductSentimentSerializer
from .forms import ReviewForm, ReviewResponseForm, UserPreferenceForm


def product_reviews(request, product_id):
    """Hiển thị đánh giá của sản phẩm"""
    # Lấy thông tin sản phẩm từ Product Service
    # TODO: Thay thế bằng API call thực tế đến Product Service
    product_data = {
        'id': product_id,
        'name': f"Product {product_id}",
    }

    # Lấy đánh giá
    reviews = Review.objects.filter(product_id=product_id).order_by('-created_at')

    # Lọc theo số sao
    rating = request.GET.get('rating')
    if rating:
        reviews = reviews.filter(rating=int(rating))

    # Lọc theo có hình ảnh
    has_images = request.GET.get('has_images')
    if has_images:
        reviews = reviews.filter(images__isnull=False).distinct()

    # Phân trang
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Tính thông kê đánh giá
    # apps/recommendation_service/views.py (tiếp)
    # Tính thông kê đánh giá
    stats = {
        'average_rating': reviews.aggregate(Avg('rating'))['rating__avg'] or 0,
        'total_reviews': reviews.count(),
        'rating_distribution': {
            '5': reviews.filter(rating=5).count(),
            '4': reviews.filter(rating=4).count(),
            '3': reviews.filter(rating=3).count(),
            '2': reviews.filter(rating=2).count(),
            '1': reviews.filter(rating=1).count(),
        }
    }

    context = {
        'product': product_data,
        'page_obj': page_obj,
        'stats': stats,
        'rating_filter': rating,
        'has_images_filter': has_images,
    }

    # Ghi log recommendation
    if request.user.is_authenticated:
        RecommendationLog.objects.create(
            user_id=request.user.id,
            product_id=product_id,
            action_type='view_reviews',
            recommendation_type='product_page',
        )

    return render(request, 'recommendation_service/product_reviews.html', context)


@login_required
def add_review(request, product_id):
    """Thêm đánh giá mới cho sản phẩm"""
    # Kiểm tra xem người dùng đã mua sản phẩm chưa
    # TODO: Kiểm tra thông qua Order Service
    verified_purchase = True

    # Kiểm tra xem người dùng đã đánh giá sản phẩm này chưa
    existing_review = Review.objects.filter(product_id=product_id, user_id=request.user.id).first()
    if existing_review:
        messages.info(request, "Bạn đã đánh giá sản phẩm này trước đó. Vui lòng cập nhật đánh giá hiện có.")
        return redirect('recommendation_service:update_review', pk=existing_review.id)

    # Lấy thông tin sản phẩm từ Product Service
    # TODO: Thay thế bằng API call thực tế đến Product Service
    product_data = {
        'id': product_id,
        'name': f"Product {product_id}",
    }

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.product_id = product_id
            review.user_id = request.user.id
            review.save()

            # Xử lý hình ảnh đã upload
            # request.FILES là một dictionary-like object
            # Nếu người dùng chọn nhiều file, request.FILES.getlist('images') sẽ trả về list các file
            for img in request.FILES.getlist('images'):
                # Xử lý từng file và lưu
                # Ví dụ:
                # image_url = handle_upload(img)  # Hàm xử lý và trả về URL
                # ReviewImage.objects.create(review=review, image_url=image_url)
                pass

            messages.success(request, "Cảm ơn bạn đã đánh giá sản phẩm!")
            return redirect('recommendation_service:product_reviews', product_id=product_id)
        else:
            messages.error(request, "Thêm đánh giá không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'product': product_data,
    }
    return render(request, 'recommendation_service/add_review.html', context)


@login_required
def update_review(request, pk):
    """Cập nhật đánh giá"""
    review = get_object_or_404(Review, pk=pk, user_id=request.user.id)

    # Lấy thông tin sản phẩm từ Product Service
    # TODO: Thay thế bằng API call thực tế đến Product Service
    product_data = {
        'id': review.product_id,
        'name': f"Product {review.product_id}",
    }

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()

            # Xử lý hình ảnh
            images = request.FILES.getlist('images')
            for image in images:
                # TODO: Upload hình ảnh và lưu URL
                image_url = f"https://example.com/review-images/{image.name}"
                ReviewImage.objects.create(review=review, image_url=image_url)

            # Cập nhật sentiment analysis
            # TODO: Phân tích sentiment từ đánh giá

            messages.success(request, "Đánh giá đã được cập nhật!")
            return redirect('recommendation_service:product_reviews', product_id=review.product_id)
        else:
            messages.error(request, "Cập nhật đánh giá không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = ReviewForm(instance=review)

    # Lấy danh sách hình ảnh hiện có
    images = review.images.all()

    context = {
        'form': form,
        'review': review,
        'product': product_data,
        'images': images,
    }
    return render(request, 'recommendation_service/update_review.html', context)


@login_required
@require_POST
def delete_review(request, pk):
    """Xóa đánh giá"""
    review = get_object_or_404(Review, pk=pk, user_id=request.user.id)
    product_id = review.product_id

    review.delete()

    # Cập nhật sentiment analysis
    # TODO: Phân tích lại sentiment

    messages.success(request, "Đánh giá đã được xóa!")
    return redirect('recommendation_service:product_reviews', product_id=product_id)


@login_required
def user_reviews(request):
    """Danh sách đánh giá của người dùng"""
    reviews = Review.objects.filter(user_id=request.user.id).order_by('-created_at')

    # Phân trang
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'recommendation_service/user_reviews.html', context)


# apps/recommendation_service/views.py (tiếp)
def recommended_products(request):
    """Hiển thị sản phẩm được đề xuất cho người dùng"""
    user_id = request.user.id if request.user.is_authenticated else None

    # Gọi API đến Product Service để lấy sản phẩm đề xuất
    # TODO: Thay thế bằng API call thực tế

    # Giả định dữ liệu
    recommended_products = []

    if user_id:
        # Lấy đề xuất dựa trên lịch sử mua hàng và hành vi người dùng
        # Phân tích đánh giá và lịch sử xem sản phẩm
        preference = UserPreference.objects.filter(user_id=user_id).first()

        if preference:
            # Lấy sản phẩm dựa trên danh mục yêu thích
            favorite_categories = preference.favorite_categories
            # TODO: Gọi API Product Service để lấy sản phẩm từ các danh mục yêu thích
    else:
        # Lấy sản phẩm phổ biến hoặc đánh giá cao
        # TODO: Gọi API Product Service
        pass

    # Ghi log recommendation
    if user_id:
        for product in recommended_products:
            RecommendationLog.objects.create(
                user_id=user_id,
                product_id=product['id'],
                action_type='recommendation_shown',
                recommendation_type='personalized',
            )

    context = {
        'products': recommended_products,
    }
    return render(request, 'recommendation_service/recommended_products.html', context)


def similar_products(request, product_id):
    """Hiển thị sản phẩm tương tự"""
    # Lấy thông tin sản phẩm từ Product Service
    # TODO: Thay thế bằng API call thực tế đến Product Service
    product_data = {
        'id': product_id,
        'name': f"Product {product_id}",
    }

    # Tìm sản phẩm tương tự
    # TODO: Gọi API Product Service để lấy sản phẩm tương tự
    similar_products = []

    # Ghi log recommendation
    if request.user.is_authenticated:
        for product in similar_products:
            RecommendationLog.objects.create(
                user_id=request.user.id,
                product_id=product['id'],
                action_type='recommendation_shown',
                recommendation_type='similar_products',
            )

    context = {
        'product': product_data,
        'similar_products': similar_products,
    }
    return render(request, 'recommendation_service/similar_products.html', context)


def frequently_bought_together(request, product_id):
    """Hiển thị sản phẩm thường được mua cùng nhau"""
    # Lấy thông tin sản phẩm từ Product Service
    # TODO: Thay thế bằng API call thực tế đến Product Service
    product_data = {
        'id': product_id,
        'name': f"Product {product_id}",
    }

    # Tìm sản phẩm thường được mua cùng
    # TODO: Phân tích dữ liệu đơn hàng để tìm ra sản phẩm mua cùng
    related_products = []

    # Ghi log recommendation
    if request.user.is_authenticated:
        for product in related_products:
            RecommendationLog.objects.create(
                user_id=request.user.id,
                product_id=product['id'],
                action_type='recommendation_shown',
                recommendation_type='frequently_bought_together',
            )

    context = {
        'product': product_data,
        'related_products': related_products,
    }
    return render(request, 'recommendation_service/frequently_bought_together.html', context)


@login_required
def based_on_history(request):
    """Đề xuất sản phẩm dựa trên lịch sử xem và mua hàng"""
    user_id = request.user.id

    # Lấy lịch sử hoạt động
    recent_logs = RecommendationLog.objects.filter(
        user_id=user_id,
        action_type__in=['view', 'click', 'add_to_cart', 'purchase']
    ).order_by('-timestamp')[:50]

    # Phân tích hành vi người dùng
    viewed_products = set()
    purchased_products = set()

    for log in recent_logs:
        if log.action_type == 'view':
            viewed_products.add(log.product_id)
        elif log.action_type == 'purchase':
            purchased_products.add(log.product_id)

    # Tìm sản phẩm liên quan
    # TODO: Gọi API Product Service để lấy sản phẩm đề xuất
    recommended_products = []

    # Ghi log recommendation
    for product in recommended_products:
        RecommendationLog.objects.create(
            user_id=user_id,
            product_id=product['id'],
            action_type='recommendation_shown',
            recommendation_type='based_on_history',
        )

    context = {
        'products': recommended_products,
    }
    return render(request, 'recommendation_service/based_on_history.html', context)


@login_required
def vendor_reviews(request):
    """Xem đánh giá sản phẩm của người bán"""
    vendor_id = request.user.id

    # Lấy danh sách sản phẩm của vendor
    # TODO: Gọi API Product Service để lấy danh sách sản phẩm
    product_ids = []  # Giả định danh sách sản phẩm

    # Lấy đánh giá
    reviews = Review.objects.filter(product_id__in=product_ids).order_by('-created_at')

    # Lọc theo sản phẩm
    product_id = request.GET.get('product_id')
    if product_id:
        reviews = reviews.filter(product_id=int(product_id))

    # Lọc theo rating
    rating = request.GET.get('rating')
    if rating:
        reviews = reviews.filter(rating=int(rating))

    # Phân trang
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'product_filter': product_id,
        'rating_filter': rating,
    }
    return render(request, 'recommendation_service/vendor/reviews.html', context)


@login_required
def respond_to_review(request, pk):
    """Phản hồi đánh giá của khách hàng"""
    vendor_id = request.user.id

    # Kiểm tra review có thuộc về sản phẩm của vendor không
    review = get_object_or_404(Review, pk=pk)

    # TODO: Xác thực quyền truy cập

    # Kiểm tra xem đã phản hồi chưa
    existing_response = ReviewResponse.objects.filter(review=review, vendor_id=vendor_id).first()

    if request.method == 'POST':
        if existing_response:
            form = ReviewResponseForm(request.POST, instance=existing_response)
        else:
            form = ReviewResponseForm(request.POST)

        if form.is_valid():
            response = form.save(commit=False)
            response.review = review
            response.vendor_id = vendor_id
            response.save()

            messages.success(request, "Phản hồi đã được gửi!")
            return redirect('recommendation_service:vendor_reviews')
        else:
            messages.error(request, "Gửi phản hồi không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        if existing_response:
            form = ReviewResponseForm(instance=existing_response)
        else:
            form = ReviewResponseForm()

    context = {
        'form': form,
        'review': review,
        'existing_response': existing_response,
    }
    return render(request, 'recommendation_service/vendor/respond_to_review.html', context)


@login_required
def user_preferences(request):
    """Xem tùy chọn sản phẩm đề xuất"""
    user_id = request.user.id
    preference, created = UserPreference.objects.get_or_create(user_id=user_id)

    # Lấy danh sách danh mục
    # TODO: Gọi API Product Service để lấy danh sách danh mục
    categories = []

    context = {
        'preference': preference,
        'categories': categories,
    }
    return render(request, 'recommendation_service/user_preferences.html', context)


@login_required
def update_preferences(request):
    """Cập nhật tùy chọn sản phẩm đề xuất"""
    user_id = request.user.id
    preference, created = UserPreference.objects.get_or_create(user_id=user_id)

    if request.method == 'POST':
        form = UserPreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()

            # Cập nhật danh mục yêu thích
            favorite_categories = request.POST.getlist('favorite_categories')
            preference.favorite_categories = favorite_categories
            preference.save()

            messages.success(request, "Tùy chọn đề xuất đã được cập nhật!")
            return redirect('recommendation_service:user_preferences')
        else:
            messages.error(request, "Cập nhật không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = UserPreferenceForm(instance=preference)

    # Lấy danh sách danh mục
    # TODO: Gọi API Product Service để lấy danh sách danh mục
    categories = []

    context = {
        'form': form,
        'preference': preference,
        'categories': categories,
    }
    return render(request, 'recommendation_service/update_preferences.html', context)


@api_view(['GET'])
def top_rated_products(request):
    """API endpoint để lấy sản phẩm đánh giá cao"""
    # Tính điểm đánh giá trung bình cho mỗi sản phẩm
    product_ratings = Review.objects.values('product_id').annotate(
        average_rating=Avg('rating'),
        review_count=Count('id')
    ).filter(review_count__gte=5).order_by('-average_rating')[:10]

    # Lấy chi tiết sản phẩm
    # TODO: Gọi API Product Service để lấy thông tin sản phẩm

    return Response(product_ratings)


@api_view(['GET'])
def sentiment_analysis(request, product_id):
    """API endpoint để lấy phân tích cảm xúc của sản phẩm"""
    try:
        sentiment = ProductSentiment.objects.get(product_id=product_id)
        serializer = ProductSentimentSerializer(sentiment)
        return Response(serializer.data)
    except ProductSentiment.DoesNotExist:
        return Response({'error': 'No sentiment analysis available for this product'}, status=404)