from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # URLs cho các API của các service
    path('api/users/', include('apps.user_service.urls')),
    path('api/products/', include('apps.product_service.urls')),
    path('api/orders/', include('apps.order_service.urls')),
    path('api/payments/', include('apps.payment_service.urls')),
    path('api/shipping/', include('apps.shipping_service.urls')),
    path('api/recommendations/', include('apps.recommendation_service.urls')),
    path('api/analytics/', include('apps.analytic_service.urls')),
    path('api/admin-service/', include('apps.admin_service.urls')),
]

# Cấu hình cho media files trong môi trường phát triển
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)