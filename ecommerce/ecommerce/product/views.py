from rest_framework import viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import Category, Brand, Product
from .serializers import CategorySerializer, BrandSerializer, ProductSerializer


class CategoryViewSet(viewsets.ViewSet):
    """
    Simple view set to view all categories
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    # @extend_schema(responses=CategorySerializer)  # 0r add serializer_class
    def list(self, request):
        serializer = CategorySerializer(self.queryset, many=True)
        return Response(serializer.data)


class BrandViewSet(viewsets.ViewSet):
    """
    Simple view set to view all brands
    """

    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

    def list(self, request):
        serializer = BrandSerializer(self.queryset, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ViewSet):
    """
    Simple view set to view all products
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # @extend_schema(responses=ProductSerializer)
    def list(self, request):
        serializer = ProductSerializer(self.queryset, many=True)
        print(serializer.data)
        return Response(serializer.data)
