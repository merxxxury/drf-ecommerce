import factory
from decimal import Decimal

from ecommerce.product.models import (
    Category,
    Brand,
    Product,
    ProductImage,
    Attribute,
    AttributeValue,
    ProductLine,
)


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    # name = 'test_category'  # this does not work because field name is unique
    name = factory.Sequence(lambda n: f'Category=_{n}')  # field from Category model
    # can be overridden directly in unit test as a parameter
    is_active = True


class BrandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Brand

    name = factory.Sequence(lambda n: f'Brand_{n}')
    is_active = True


class AttributeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Attribute

    name = factory.Faker('word')


class AttributeValueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AttributeValue

    value = factory.Sequence(lambda n: f'Value_{n}')
    attribute_id = factory.SubFactory(
        AttributeFactory
    )  # Links to an Attribute instance


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f'Product_{n}')
    slug = factory.Faker('slug')
    description = factory.Faker('sentence')
    is_matcha = True
    category_id = factory.SubFactory(CategoryFactory)
    brand_id = factory.SubFactory(BrandFactory)
    is_active = True


class ProductLineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductLine

    price = Decimal('19.99')
    second_name = factory.Faker('word')
    second_description = factory.Faker('sentence')
    slug = factory.Faker('slug')
    sku = factory.Sequence(lambda n: f'SKU-{n}')
    quantity = 10
    product_id = factory.SubFactory(ProductFactory)
    is_active = True
    display_order = factory.Sequence(lambda n: n)

    @factory.post_generation
    def attributes(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for attribute in extracted:
                self.attributes.add(attribute)
        else:
            self.attributes.add(AttributeValueFactory())


class ProductImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductImage

    name = factory.Faker('word')  # Random word for name
    alternative_text = factory.Faker('sentence')  # Random sentence for alt text
    location = factory.Faker('url')  # Random URL for location
    product_line_id = factory.SubFactory(
        ProductLineFactory
    )  # Links to a ProductLine instance
