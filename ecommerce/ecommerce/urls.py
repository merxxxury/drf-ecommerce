from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .product import views


router = DefaultRouter()
router.register(r'category', views.CategoryViewSet, basename='category')
router.register(r'brand', views.BrandViewSet)
router.register(r'product', views.ProductViewSet, basename='product')
router.register(r'product-line', views.ProductLineViewSet, basename='product_line')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/schema/swagger-ui/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
]
