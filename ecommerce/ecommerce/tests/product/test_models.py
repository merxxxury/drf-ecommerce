import pytest
from django.core.exceptions import ValidationError


# pytestmark = pytest.mark.django_db  # use this specific variable to get access to db
# or use decorator


@pytest.mark.django_db
class TestCategoryModel:
    def test_str_method(self, category_factory):
        # category_factory is specific variable
        # created from name of factory class but lowercase and _ before capital letters

        # Test Structure:
        # Arrange
        # Act
        obj = category_factory(name='category1_test')
        # Assert
        assert obj.__str__() == 'category1_test'


@pytest.mark.django_db
class TestBrandModel:
    def test_str_method(self, brand_factory):
        obj = brand_factory(name='brand1_test')
        assert obj.__str__() == 'brand1_test'


@pytest.mark.django_db
class TestProductModel:
    def test_product_creation(self, product_factory):
        obj = product_factory(
            name='product1_test', description='desc1_test', is_matcha=True
        )
        assert obj.name == 'product1_test'
        assert obj.description == 'desc1_test'
        assert obj.is_matcha is True
        assert obj.category_id is not None
        assert obj.brand_id is not None
        assert obj.product_type_id is not None

    def test_str_method(self, product_factory):
        obj = product_factory()
        assert obj.__str__() == obj.name


@pytest.mark.django_db
class TestProductLineModel:
    def test_str_method(self, product_line_factory, attribute_value_factory):
        attrs = attribute_value_factory()
        obj = product_line_factory(attributes=(attrs,))
        assert obj.__str__() == f'{obj.product_id.name} - {obj.sku}'

    DISPLAY_ORDER = 5

    def test_duplicate_display_order(self, product_line_factory, product_factory):
        product = product_factory()
        product_line_factory(display_order=self.DISPLAY_ORDER, product_id=product)

        with pytest.raises(ValidationError) as excinfo:
            product_line_factory(display_order=self.DISPLAY_ORDER, product_id=product)

        assert excinfo.value.message_dict['display_order'] == [
            f'The display order "{self.DISPLAY_ORDER}" is already in use for this product. Please choose a different value.'
        ]

    def test_display_order_unique_across_different_products(
        self, product_line_factory, product_factory
    ):
        product_1 = product_factory()
        product_2 = product_factory()

        product_line_factory(display_order=1, product_id=product_1)
        product_line_2 = product_line_factory(display_order=1, product_id=product_2)

        assert product_line_2 is not None


@pytest.mark.django_db
class TestAttributeModel:
    def test_str_method(self, attribute_factory):
        obj = attribute_factory(name='Attr_1')
        assert obj.__str__() == 'Attr_1'


@pytest.mark.django_db
class TestAttributeValueModel:
    def test_str_method(self, attribute_value_factory):
        obj = attribute_value_factory(value='AttrValue_1')
        assert obj.__str__() == f'{obj.attribute_id.name}: {obj.value}'


@pytest.mark.django_db
class TestProductImageModel:
    def test_str_method(
        self, product_image_factory, product_factory, product_line_factory
    ):
        product = product_factory(name='Product_99')
        product_line = product_line_factory(
            product_id=product, slug='product-line-99', sku='sku123'
        )
        obj = product_image_factory(
            alternative_text='Image_1', product_line_id=product_line, display_order=1
        )
        assert obj.__str__() == f'pl_{product_line.slug}/order_{obj.display_order}'


@pytest.mark.django_db
class TestProductTypeModel:
    def test_str_method(self, product_type_factory, attribute_factory):
        attribute = attribute_factory(name='Attribute_1')
        product_type = product_type_factory(attributes=(attribute,))
        assert str(product_type) == product_type.type_name
