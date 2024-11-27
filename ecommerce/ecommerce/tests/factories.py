import factory
from decimal import Decimal

from faker.generator import random

from ecommerce.product.models import (
    Category,
    Product,
    ProductImage,
    Attribute,
    AttributeValue,
    ProductLine,
    ProductType,
)


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f'Category_{n}')  # field from Category model
    slug = factory.Sequence(lambda n: f'category-{n}')
    is_active = False
    # can be overridden directly in unit test as a parameter


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


class ProductTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductType
        skip_postgeneration_save = True

    type_name = factory.Faker('word')

    @factory.post_generation
    def parent(self, create, extracted, **kwargs):
        if extracted:
            self.parent = extracted
            if create:
                self.save()

    @factory.post_generation
    def attributes(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.attributes.add(*extracted)


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product
        skip_postgeneration_save = True

    name = factory.Sequence(lambda n: f'Product_{n}')
    slug = factory.Faker('slug')
    pid = factory.Sequence(lambda n: f'00000{n}')
    description = factory.Faker('sentence')
    category_id = factory.SubFactory(CategoryFactory)
    product_type_id = factory.SubFactory(ProductTypeFactory)

    @factory.post_generation
    def attribute_values(self, created, extracted, **kwargs):
        if not created or not extracted:
            return
        self.attribute_values.add(*extracted)
        self.save()


class ProductLineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductLine
        skip_postgeneration_save = True

    display_order = factory.Sequence(lambda n: n)
    price = factory.LazyFunction(lambda: round(random.uniform(1, 10000), 2))
    slug = factory.Faker('slug')
    second_name = factory.Faker('word')
    second_description = factory.Faker('sentence')
    sku = factory.Sequence(lambda n: f'SKU-{n}')
    # weight = factory.LazyFunction(lambda: round(random.uniform(0, 100), 3))
    product_id = factory.SubFactory(ProductFactory)
    product_type_id = factory.SubFactory(ProductTypeFactory)

    @factory.post_generation
    def attributes(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.attributes.add(*extracted)
        self.save()


class ProductImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductImage

    alternative_text = factory.Faker('sentence')  # Random sentence for alt text
    url = factory.Faker('url')  # Random URL for location
    product_line_id = factory.SubFactory(ProductLineFactory)
