import pytest


# pytestmark = pytest.mark.django_db  # use this specific variable to get access to db
# or use decorator


@pytest.mark.django_db
class TestCategoryModel:
    def test_str_method(self, category_factory):
        # category_factory is specific variable
        # created from name of factory class but lowercase and _ instead of whitespace

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

    def test_str_method(self, product_factory):
        obj = product_factory(name='product2_test')
        assert obj.__str__() == 'product2_test'
