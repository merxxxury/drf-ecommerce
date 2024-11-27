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


class AttributeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attribute
        fields = '__all__'


class AttributeValueSerializer(serializers.ModelSerializer):
    attribute_id = AttributeSerializer(read_only=True)

    class Meta:
        model = AttributeValue
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        exclude = ['id', 'product_line_id']


class ProductLineSerializer(serializers.ModelSerializer):
    attributes = AttributeValueSerializer(many=True, read_only=True)
    # related_name='product_image' in ProductImage model to ProductLine model
    product_image = ProductImageSerializer(many=True)

    class Meta:
        model = ProductLine
        # fields = '__all__'
        fields = [
            'price',
            'slug',
            'second_name',
            'second_description',
            'quantity',
            'sku',
            'attributes',
            'display_order',
            'is_active',
            'product_image',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if data['attributes']:
            # flatting json
            flatten_attributes = {}
            for item in data['attributes']:
                # print(item)
                if item['attribute_id']['id'] in flatten_attributes:
                    raise ValueError(
                        f"Attribute with name \"{item['attribute_id']['id']}\" already exists"
                    )
                else:
                    flatten_attributes.update(
                        {item['attribute_id']['id']: item['value']}
                    )
            data['attributes'] = flatten_attributes
        else:
            data.pop('attributes', None)

        data = remove_empty_fields(data, ['second_name', 'second_description'])
        return data


class ProductSerializer(serializers.ModelSerializer):
    # FLATTEN. source 'category_id' here is field in Product model
    category_name = serializers.CharField(source='category_id.name', read_only=True)
    category_slug = serializers.CharField(source='category_id.slug', read_only=True)

    # product_line is related name in ProductLine model
    product_line = serializers.SerializerMethodField()
    product_attributes = serializers.SerializerMethodField()

    class Meta:
        model = Product
        # fields = '__all__'
        fields = [
            'name',
            'slug',
            'description',
            'description',
            'category_name',
            'category_slug',
            'product_line',
            'product_attributes',
        ]

    def get_product_line(self, obj):
        active_product_lines = obj.product_line.filter(is_active=True)
        return ProductLineSerializer(active_product_lines, many=True).data

    def get_product_attributes(self, obj):
        # func syntax: get_<field_name> or specify any name in method_name parameter
        # returns the attributes defined in the ProductType model for specific product
        product_attributes = Attribute.objects.filter(
            product_type_attribute__product_type=obj.id
        )
        return AttributeSerializer(product_attributes, many=True).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        flatten_product_attributes = {}
        if data['product_attributes']:
            for item in data['product_attributes']:
                flatten_product_attributes.update({item['id']: item['name']})
            data['product_attributes'] = flatten_product_attributes

        return data
