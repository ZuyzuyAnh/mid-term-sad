from django.urls import path
from . import views

app_name = 'order_service'

urlpatterns = [
    # Cart Management
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),

    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/shipping/', views.checkout_shipping, name='checkout_shipping'),
    path('checkout/payment/', views.checkout_payment, name='checkout_payment'),
    path('checkout/complete/', views.checkout_complete, name='checkout_complete'),

    # Order Management
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/cancel/', views.cancel_order, name='cancel_order'),

    # Wishlist
    path('wishlist/', views.view_wishlist, name='view_wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/move-to-cart/<int:item_id>/', views.move_to_cart, name='move_to_cart'),

    # Vendor Order Management
    path('vendor/orders/', views.vendor_orders, name='vendor_orders'),
    path('vendor/orders/<int:pk>/', views.vendor_order_detail, name='vendor_order_detail'),
    path('vendor/orders/<int:pk>/update-status/', views.update_order_status, name='update_order_status'),

    # Order API
    path('api/cart-count/', views.cart_item_count, name='cart_item_count'),
    path('api/order-status/<int:order_id>/', views.get_order_status, name='get_order_status'),
]