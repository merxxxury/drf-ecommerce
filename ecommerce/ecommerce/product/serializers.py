from rest_framework import serializers
from .models import *


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        # fields = '__all__'
        fields = ['id', 'name']


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    brand_id = BrandSerializer(read_only=True)
    category_id = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
