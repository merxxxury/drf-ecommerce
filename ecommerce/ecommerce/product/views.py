from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import connection


from .utils import inspect_queries


from .models import Category, Brand, Product, ProductLine
from .serializers import (
    CategorySerializer,
    BrandSerializer,
    ProductSerializer,
    ProductLineSerializer,
)


class CategoryViewSet(viewsets.ViewSet):
    """
    Simple view set to view all categories
    """

    queryset = Category.active.all()
    serializer_class = CategorySerializer

    # @extend_schema(responses=CategorySerializer)  # 0r add serializer_class
    def list(self, request):
        serializer = CategorySerializer(self.queryset, many=True)
        return Response(serializer.data)


class BrandViewSet(viewsets.ViewSet):
    """
    Simple view set to view all brands
    """

    queryset = Brand.active.all()
    serializer_class = BrandSerializer

    def list(self, request):
        serializer = BrandSerializer(self.queryset, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ViewSet):
    """
    Simple view set to view all products,
    and all products by category
    """

    queryset = (
        Product.active.all()
        .select_related('category_id', 'brand_id')
        .prefetch_related(
            'product_line__attributes__attribute_id',
            'product_line__product_image',
        )
    )

    serializer_class = ProductSerializer
    lookup_field = 'slug'

    def retrieve(self, request, slug=None):
        serializer = ProductSerializer(self.queryset.filter(slug=slug), many=True)

        data = Response(serializer.data)
        # function from utils.py to inspect queries
        # print(inspect_queries(connection.queries))

        return data

    def list(self, request):
        connection.queries.clear()

        serializer = ProductSerializer(
            self.queryset,
            many=True,
        )
        data = Response(serializer.data)

        # print (inspect_queries(connection.queries))
        return data

    @action(
        detail=False,
        methods=['get'],
        url_path='category/(?P<category_slug>[\w-]+)',
    )
    def list_by_category_slug(self, request, category_slug=None):
        products_by_category = self.queryset.filter(category_id__slug=category_slug)
        serializer = ProductSerializer(products_by_category, many=True)

        data = Response(serializer.data)
        # print (inspect_queries(connection.queries))
        return data


class ProductLineViewSet(viewsets.ViewSet):
    """
    A simple view set to viewing the list of product lines
    and retrieving details for a single product line
    """

    queryset = ProductLine.active.all()
    serializer_class = ProductLineSerializer

    def list(self, request):
        serializer = ProductLineSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        product_line = self.queryset.filter(pk=pk)
        serializer = ProductLineSerializer(product_line, many=True)
        return Response(serializer.data)
