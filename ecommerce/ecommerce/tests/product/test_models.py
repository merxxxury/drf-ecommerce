from decimal import InvalidOperation, Decimal

import pytest
from django.db.utils import DataError
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.db.utils import IntegrityError

from ecommerce.product.models import (
    Category,
    Product,
    ProductLine,
    ProductImage,
    ProductLineAttributeValue,
)


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

    def test_name_max_length(self, category_factory):
        long_name = 'n' * 151
        with pytest.raises(
            DataError, match=r"value too long for type character varying\(150\)"
        ):
            category_factory(name=long_name)

    def test_slug_max_length(self, category_factory):
        long_slug = 's' * 256
        with pytest.raises(
            DataError, match=r"value too long for type character varying\(255\)"
        ):
            category_factory(slug=long_slug)

    def test_unique_name_field(self, category_factory):
        category_factory(name='unique_name')
        with pytest.raises(IntegrityError):
            category_factory(name='unique_name')

    def test_is_active_default_false(self, category_factory):
        obj = category_factory()
        assert obj.is_active is False

    def test_parent_on_delete_protect(self, category_factory):
        parent_obj = category_factory(name='parent_category')
        category_factory(parent=parent_obj)

        with pytest.raises(ProtectedError):
            parent_obj.delete()

    def test_parent_null(self, category_factory):
        obj = category_factory()
        assert obj.parent is None

    def test_returning_only_is_active_true(self, category_factory):
        category_factory(is_active=True)
        category_factory(is_active=False)
        qs = Category.active.count()
        assert qs == 1

    def test_returning_all(self, category_factory):
        category_factory(is_active=True)
        category_factory(is_active=False)
        qs = Category.objects.count()
        assert qs == 2


@pytest.mark.django_db
class TestProductModel:
    def test_product_creation(self, product_factory):
        obj = product_factory(name='product1_test', description='desc1_test')
        assert obj.name == 'product1_test'
        assert obj.description == 'desc1_test'
        assert obj.is_digital is False
        assert obj.category_id is not None

    def test_str_method(self, product_factory):
        obj = product_factory()
        assert obj.__str__() == obj.name

    def test_name_max_length(self, product_factory):
        long_name = 'n' * 201
        with pytest.raises(
            DataError, match=r"value too long for type character varying\(200\)"
        ):
            product_factory(name=long_name)

    def test_name_uniqueness(self, product_factory):
        name = 'some_name'
        product_factory(name=name)
        with pytest.raises(IntegrityError):
            product_factory(name=name)

    def test_slug_max_length(self, product_factory):
        long_slug = 's' * 251
        with pytest.raises(
            DataError, match=r"value too long for type character varying\(250\)"
        ):
            product_factory(slug=long_slug)

    def test_slug_uniqueness(self, product_factory):
        slug = 'some_slug'
        product_factory(slug=slug)
        with pytest.raises(IntegrityError):
            product_factory(slug=slug)

    def test_pid_max_length(self, product_factory):
        long_pid = 's' * 11
        with pytest.raises(
            DataError, match=r"value too long for type character varying\(10\)"
        ):
            product_factory(pid=long_pid)

    def test_pid_uniqueness(self, product_factory):
        pid = '0000001'
        product_factory(pid=pid)
        with pytest.raises(IntegrityError):
            product_factory(pid=pid)

    def test_description_allows_blank(self, product_factory):
        obj = product_factory(name='')
        assert obj.name == ''

        obj.save()
        assert Product.objects.filter(name="").exists()

    def test_deleting_category_protect(self, category_factory, product_factory):
        obj_category = category_factory()
        product_factory(category_id=obj_category)
        with pytest.raises(ProtectedError):
            obj_category.delete()

    def test_is_active_default_false(self, product_factory):
        obj = product_factory()
        assert obj.is_active is False

    def test_returning_only_is_active_true(self, product_factory):
        product_factory(is_active=False)
        product_factory(is_active=True)
        qs = Product.active.all().count()
        assert qs == 1

    def test_returning_all_objects(self, product_factory):
        product_factory(is_active=False)
        product_factory(is_active=True)
        qs = Product.objects.all().count()
        assert qs == 2

    def test_attribute_values_addition(self, product_factory, attribute_value_factory):
        product = product_factory()
        attr_value1 = attribute_value_factory()
        attr_value2 = attribute_value_factory()

        # Add attribute values to product
        product.attribute_values.add(attr_value1, attr_value2)

        assert product.attribute_values.count() == 2
        assert attr_value1 in product.attribute_values.all()
        assert attr_value2 in product.attribute_values.all()

    def test_attribute_values_removal(self, product_factory, attribute_value_factory):
        product = product_factory()
        attr_value = attribute_value_factory()

        # Add and then remove an attribute value
        product.attribute_values.add(attr_value)
        assert product.attribute_values.count() == 1

        product.attribute_values.remove(attr_value)
        assert product.attribute_values.count() == 0

    def test_attribute_values_clear(self, product_factory, attribute_value_factory):
        product = product_factory()
        attr_value1 = attribute_value_factory()
        attr_value2 = attribute_value_factory()

        # Add attribute values and then clear them
        product.attribute_values.add(attr_value1, attr_value2)
        assert product.attribute_values.count() == 2

        product.attribute_values.clear()
        assert product.attribute_values.count() == 0

    def test_attribute_values_duplicate_prevention(
        self, product_factory, attribute_value_factory
    ):
        product = product_factory()
        attr_value = attribute_value_factory()

        # Add the same attribute value twice
        product.attribute_values.add(attr_value)
        product.attribute_values.add(attr_value)

        # Assert no duplicates
        assert product.attribute_values.count() == 1


@pytest.mark.django_db
class TestProductLineModel:
    def test_str_method(self, product_line_factory, product_factory):
        product = product_factory(name='product_name')
        obj = product_line_factory(product_id=product, sku='123')
        assert obj.__str__() == 'product_name - 123'

    DISPLAY_ORDER = 5

    def test_duplicate_display_order(self, product_line_factory, product_factory):
        product = product_factory()
        product_line_factory(display_order=self.DISPLAY_ORDER, product_id=product)

        with pytest.raises(ValidationError) as excinfo:
            product_line_factory(display_order=self.DISPLAY_ORDER, product_id=product)

        assert excinfo.value.message_dict['display_order'] == [
            f'The display order "{self.DISPLAY_ORDER}" is already in use. Please choose a different value.'
        ]

    def test_display_order_unique_across_different_products(
        self, product_line_factory, product_factory
    ):
        product_1 = product_factory()
        product_2 = product_factory()

        product_line_factory(display_order=self.DISPLAY_ORDER, product_id=product_1)
        product_line_2 = product_line_factory(
            display_order=self.DISPLAY_ORDER, product_id=product_2
        )

        assert product_line_2 is not None
        assert product_line_2.display_order == self.DISPLAY_ORDER

    def test_price_max_digits(self, product_line_factory):
        with pytest.raises(DataError, match=r'numeric field overflow'):
            product_line_factory(price=123456.78)

    def test_price_decimal_place_rounding(self, product_line_factory):
        obj1 = product_line_factory(price=123.455)
        assert obj1.price == Decimal(str(123.45))

        obj2 = product_line_factory(price=123.4555)
        assert obj2.price == Decimal(str(123.46))

        obj3 = product_line_factory(price=123.4914563)
        assert obj3.price == Decimal(str(123.49))

        obj4 = product_line_factory(price=123.99999)
        assert obj4.price == Decimal(str(124.00))

        obj5 = product_line_factory(price=444.00)
        assert obj5.price == Decimal(str(444.00))

    def test_slug_max_length(self, product_line_factory):
        long_slug = 's' * 251
        with pytest.raises(
            DataError, match=r"value too long for type character varying\(250\)"
        ):
            product_line_factory(slug=long_slug)

    def test_slug_uniqueness(self, product_line_factory):
        slug = 'some_slug'
        product_line_factory(slug=slug)
        with pytest.raises(IntegrityError):
            product_line_factory(slug=slug)

    def test_is_active_default_false(self, product_line_factory):
        obj = product_line_factory()
        assert obj.is_active is False

    def test_returning_only_is_active_true(self, product_line_factory):
        product_line_factory(is_active=False)
        product_line_factory(is_active=True)
        qs = ProductLine.active.all().count()
        assert qs == 1

    def test_returning_all_objects(self, product_line_factory):
        product_line_factory(is_active=False)
        product_line_factory(is_active=True)
        qs = ProductLine.objects.all().count()
        assert qs == 2

    def test_second_name_max_length(self, product_line_factory):
        long_second_name = 'n' * 201
        with pytest.raises(
            DataError, match=r"value too long for type character varying\(200\)"
        ):
            product_line_factory(second_name=long_second_name)

    def test_second_name_allows_blank(self, product_line_factory):
        blank = ''
        obj = product_line_factory(second_name=blank)
        assert obj.second_name == ''

        obj.save()
        assert ProductLine.objects.filter(second_name='').exists()

    def test_second_description_max_length(self, product_line_factory):
        long_second_desc = 'd' * 256
        with pytest.raises(
            DataError, match=r"value too long for type character varying\(255\)"
        ):
            product_line_factory(second_description=long_second_desc)

    def test_second_description_allows_blank(self, product_line_factory):
        blank = ''
        obj = product_line_factory(second_description=blank)
        assert obj.second_description == ''

        obj.save()
        assert ProductLine.objects.filter(second_description='').exists()

    def test_sku_max_length(self, product_line_factory):
        long_sku = 'd' * 251
        with pytest.raises(
            DataError, match=r"value too long for type character varying\(250\)"
        ):
            product_line_factory(sku=long_sku)

    def test_sku_uniqueness(self, product_line_factory):
        sku = 'some_slug'
        product_line_factory(sku=sku)
        with pytest.raises(IntegrityError):
            product_line_factory(sku=sku)

    def test_quantity_default(self, product_line_factory):
        obj = product_line_factory()
        assert obj.quantity == 1

    def test_weight_max_digits(self, product_line_factory):
        with pytest.raises(DataError, match=r'numeric field overflow'):
            product_line_factory(weight=123456.789)

    def test_weight_field(self, product_line_factory):
        obj1 = product_line_factory(weight=123.45)
        assert obj1.weight == Decimal(str(123.450))

        obj2 = product_line_factory()
        assert obj2.weight == Decimal(str(0.000))

        obj3 = product_line_factory(weight=123.1119999999999)
        assert obj3.weight == Decimal(str(123.112))

        obj4 = product_line_factory(weight=0.9)
        assert obj4.weight == Decimal(str(0.900))

        obj5 = product_line_factory(weight=000.9)
        assert obj5.weight == Decimal(str(0.900))

    def test_deleting_product_protect(self, product_line_factory, product_factory):
        obj_product = product_factory()
        product_line_factory(product_id=obj_product)
        with pytest.raises(ProtectedError):
            obj_product.delete()

    def test_deleting_product_type_id_protect(
        self, product_line_factory, product_type_factory
    ):
        obj_product_type = product_type_factory()
        product_line_factory(product_type_id=obj_product_type)
        with pytest.raises(ProtectedError):
            obj_product_type.delete()


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

    def test_alternative_text_max_length(self, product_image_factory):
        long_text = 't' * 251
        with pytest.raises(
            DataError, match=r"value too long for type character varying\(250\)"
        ):
            product_image_factory(alternative_text=long_text)

    def test_alternative_text_allows_blank(self, product_image_factory):
        obj = product_image_factory(alternative_text='')
        assert obj.alternative_text == ''

        obj.save()
        assert ProductImage.objects.filter(alternative_text="").exists()

    DISPLAY_ORDER = 2

    def test_duplicate_display_order(self, product_line_factory, product_image_factory):
        product_line = product_line_factory()
        product_image_factory(
            display_order=self.DISPLAY_ORDER, product_line_id=product_line
        )

        with pytest.raises(ValidationError) as excinfo:
            product_image_factory(
                display_order=self.DISPLAY_ORDER, product_line_id=product_line
            )

        assert excinfo.value.message_dict['display_order'] == [
            f'The display order "{self.DISPLAY_ORDER}" is already in use. Please choose a different value.'
        ]

    def test_display_order_unique_across_different_products(
        self, product_line_factory, product_image_factory
    ):
        product_line_1 = product_line_factory()
        product_line_2 = product_line_factory()

        product_image_factory(
            display_order=self.DISPLAY_ORDER, product_line_id=product_line_1
        )
        product_line_2 = product_image_factory(
            display_order=self.DISPLAY_ORDER, product_line_id=product_line_2
        )

        assert product_line_2 is not None
        assert product_line_2.display_order == self.DISPLAY_ORDER


@pytest.mark.django_db
class TestProductTypeModel:
    def test_str_method(self, product_type_factory):
        # attribute = attribute_factory(name='Attribute_1')
        # product_type = product_type_factory(attributes=(attribute,))
        obj = product_type_factory(type_name='test_type_name')
        assert str(obj) == 'test_type_name'

    def test_type_name_max_length(self, product_type_factory):
        long_type_name = 'n' * 151
        with pytest.raises(
            DataError, match=r"value too long for type character varying\(150\)"
        ):
            product_type_factory(type_name=long_type_name)

    def test_parent_on_delete_protect(self, product_type_factory):
        parent_obj = product_type_factory(type_name='parent_type')
        product_type_factory(parent=parent_obj)

        with pytest.raises(ProtectedError):
            parent_obj.delete()


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

    def test_value_max_length(self, attribute_value_factory):
        long_value = 'v' * 101
        with pytest.raises(
            DataError, match=r"value too long for type character varying\(100\)"
        ):
            attribute_value_factory(value=long_value)

    def test_value_blank_impossible(self, attribute_value_factory):
        obj = attribute_value_factory(value='')
        with pytest.raises(ValidationError):
            obj.full_clean()

    def test_attribute_id_fk(self, attribute_value_factory, attribute_factory):
        attr = attribute_factory(name='color')
        obj = attribute_value_factory(attribute_id=attr)
        assert obj.attribute_id.name == 'color'

        with pytest.raises(ValueError):
            attribute_value_factory(attribute_id=1)


@pytest.mark.django_db
class TestProductLineAttributeValue:
    def test_clean_valid_attribute(
        self, product_line_factory, attribute_value_factory, product_type_factory
    ):
        # Create a ProductType with specific attributes
        product_type = product_type_factory(
            attributes=[
                attribute_value_factory(attribute_id__name="Color").attribute_id
            ]
        )
        product_line = product_line_factory(product_type_id=product_type)
        valid_attribute = attribute_value_factory(attribute_id__name="Color")

        # Create ProductLineAttributeValue with valid data
        product_line_attribute_value = ProductLineAttributeValue(
            product_line=product_line,
            attribute_value=valid_attribute,
        )

        # Should not raise any errors
        product_line_attribute_value.clean()

    def test_clean_invalid_attribute(
        self, product_line_factory, attribute_value_factory, product_type_factory
    ):
        # Create a ProductType with specific attributes
        product_type = product_type_factory(
            attributes=[
                attribute_value_factory(attribute_id__name="Color").attribute_id
            ]
        )
        product_line = product_line_factory(product_type_id=product_type)
        invalid_attribute = attribute_value_factory(attribute_id__name="Size")

        # Create ProductLineAttributeValue with invalid data
        product_line_attribute_value = ProductLineAttributeValue(
            product_line=product_line,
            attribute_value=invalid_attribute,
        )

        # Should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            product_line_attribute_value.clean()
        assert "not allowed for product lines of type" in str(exc_info.value)

    def test_clean_duplicate_attribute(
        self, product_line_factory, attribute_value_factory, product_type_factory
    ):
        # Create a ProductType and ProductLine
        product_type = product_type_factory(
            attributes=[
                attribute_value_factory(attribute_id__name="Color").attribute_id
            ]
        )
        product_line = product_line_factory(product_type_id=product_type)
        attribute = attribute_value_factory(attribute_id__name="Color")

        # Create an initial ProductLineAttributeValue
        ProductLineAttributeValue.objects.create(
            product_line=product_line,
            attribute_value=attribute,
        )

        # Attempt to create a duplicate
        duplicate_attribute_value = ProductLineAttributeValue(
            product_line=product_line,
            attribute_value=attribute,
        )

        # Should raise ValidationError for duplicates
        with pytest.raises(ValidationError) as exc_info:
            duplicate_attribute_value.clean()
        assert "already exists for this product line" in str(exc_info.value)

    def test_save_valid_attribute(
        self, product_line_factory, attribute_value_factory, product_type_factory
    ):
        # Create a ProductType with specific attributes
        product_type = product_type_factory(
            attributes=[
                attribute_value_factory(attribute_id__name="Color").attribute_id
            ]
        )
        product_line = product_line_factory(product_type_id=product_type)
        valid_attribute = attribute_value_factory(attribute_id__name="Color")

        # Create and save ProductLineAttributeValue
        product_line_attribute_value = ProductLineAttributeValue(
            product_line=product_line,
            attribute_value=valid_attribute,
        )

        # Save should work without issues as clean() is called in save()
        product_line_attribute_value.save()

        # Ensure it exists in the database
        assert ProductLineAttributeValue.objects.filter(
            product_line=product_line, attribute_value=valid_attribute
        ).exists()

    def test_save_invalid_attribute(
        self, product_line_factory, attribute_value_factory, product_type_factory
    ):
        # Create a ProductType with specific attributes
        product_type = product_type_factory(
            attributes=[
                attribute_value_factory(attribute_id__name="Color").attribute_id
            ]
        )
        product_line = product_line_factory(product_type_id=product_type)
        invalid_attribute = attribute_value_factory(attribute_id__name="Size")

        # Create ProductLineAttributeValue with invalid data
        product_line_attribute_value = ProductLineAttributeValue(
            product_line=product_line,
            attribute_value=invalid_attribute,
        )

        # Save should raise ValidationError because clean() is called in save()
        with pytest.raises(ValidationError) as exc_info:
            product_line_attribute_value.save()
        assert "not allowed for product lines of type" in str(exc_info.value)

    def test_str_method(
        self,
        attribute_factory,
        attribute_value_factory,
        product_factory,
        product_line_factory,
        product_type_factory,
    ):
        # Arrange: Create an instance of ProductLineAttributeValue

        attribute = attribute_factory(name='Color')
        attribute_value = attribute_value_factory(value="Green", attribute_id=attribute)
        product = product_factory(name='Product-100')

        product_type = product_type_factory(attributes=[attribute_value.attribute_id])
        product_line = product_line_factory(
            product_type_id=product_type, product_id=product, sku="SKU-100"
        )
        product_line_attribute_value = ProductLineAttributeValue.objects.create(
            product_line=product_line,
            attribute_value=attribute_value,
        )
        # Act: Call the __str__ method
        str_tested = str(product_line_attribute_value)

        # Assert: Verify the string representation
        str_expected = 'Color: Green, Product-100 - SKU-100'
        assert (
            str_tested == str_expected
        ), f"Expected: '{str_expected}', but got: '{str_tested}'"
