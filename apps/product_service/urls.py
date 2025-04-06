from django.urls import path
from . import views

app_name = 'product_service'

urlpatterns = [
    # Product Browsing
    path('', views.product_list, name='product_list'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path('slug/<slug:slug>/', views.product_detail_by_slug, name='product_detail_by_slug'),
    path('search/', views.product_search, name='product_search'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>/', views.category_detail, name='category_detail'),
    path('categories/slug/<slug:slug>/', views.category_detail_by_slug, name='category_detail_by_slug'),

    # Vendor Product Management
    path('vendor/products/', views.vendor_products, name='vendor_products'),
    path('vendor/products/create/', views.product_create, name='product_create'),
    path('vendor/products/<int:pk>/update/', views.product_update, name='product_update'),
    path('vendor/products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # Inventory Management
    path('vendor/inventory/', views.inventory_list, name='inventory_list'),
    path('vendor/inventory/<int:pk>/update/', views.inventory_update, name='inventory_update'),

    # Product Attributes
    path('attributes/', views.attribute_list, name='attribute_list'),
    path('attributes/<int:pk>/', views.attribute_detail, name='attribute_detail'),
    path('products/<int:pk>/attributes/', views.product_attributes, name='product_attributes'),

    # Product API
    path('api/trending/', views.trending_products, name='trending_products'),
    path('api/new-arrivals/', views.new_arrivals, name='new_arrivals'),
    path('api/discounted/', views.discounted_products, name='discounted_products'),
]