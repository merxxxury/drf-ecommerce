import factory

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


class BrandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Brand

    name = factory.Sequence(lambda n: f'Brand_{n}')


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f'Product_{n}')
    description = factory.Sequence(lambda n: f'description_{n}')
    is_matcha = True
    category_id = factory.SubFactory(CategoryFactory)
    brand_id = factory.SubFactory(BrandFactory)
