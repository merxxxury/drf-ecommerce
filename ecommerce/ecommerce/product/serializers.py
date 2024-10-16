from rest_framework import serializers
from .models import *
from .utils import remove_empty_fields


class CategorySerializer(serializers.ModelSerializer):
    # category_name: any name
    # the source need to be the same as in the model
    category_name = serializers.CharField(source='name')

    class Meta:
        model = Category
        # fields = '__all__'
        fields = ['category_name', 'slug']


class BrandSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='name')

    class Meta:
        model = Brand
        fields = ['brand_name']
        # exclude = ['id']


class AttributeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attribute
        # fields = '__all__'
        exclude = ['id']


class AttributeValueSerializer(serializers.ModelSerializer):
    attribute_id = AttributeSerializer(read_only=True)

    class Meta:
        model = AttributeValue
        # fields = '__all__'
        exclude = ['id']


class ProductLineSerializer(serializers.ModelSerializer):
    # product_id = ProductSerializer(read_only=True)
    attributes = AttributeValueSerializer(many=True, read_only=True)

    class Meta:
        model = ProductLine
        # fields = '__all__'
        exclude = ['id', 'product_id', 'created_at', 'updated_at', 'is_active']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # deletion attributes value if it is empty
        if data['attributes']:
            # flatting json
            flatten_attributes = {
                item['attribute_id']['name']: item['value']
                for item in data['attributes']
            }
            data['attributes'] = flatten_attributes
        else:
            data.pop('attributes', None)

        data = remove_empty_fields(data, ['second_name', 'second_description'])
        return data


class ProductSerializer(serializers.ModelSerializer):
    # FLATTEN. source 'brand_id' here is field in Product model
    brand_name = serializers.CharField(source='brand_id.name')
    # brand_id = BrandSerializer(read_only=True)
    category_name = serializers.CharField(source='category_id.name', read_only=True)
    category_slug = serializers.CharField(source='category_id.slug', read_only=True)
    # category_name = serializers.CharField(source='name')

    # product_line is related name in ProductLine model
    product_line = ProductLineSerializer(many=True)

    class Meta:
        model = Product
        # fields = '__all__'
        fields = [
            'name',
            'slug',
            'description',
            'brand_name',
            "category_name",
            'category_slug',
            'product_line',
        ]
