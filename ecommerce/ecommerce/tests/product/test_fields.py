import pytest
from django.core.exceptions import ValidationError
from ecommerce.tests.factories import (
    ProductFactory,
    ProductLineFactory,
    CategoryFactory,
    ProductTypeFactory,
)


@pytest.mark.django_db
class TestOrderingField:
    def test_ordering_field_assignment(self):
        """Ensure the OrderingField assigns the correct order based on unique_for_field."""
        category = CategoryFactory()
        product_type = ProductTypeFactory()
        product = ProductFactory(category_id=category, product_type_id=product_type)
        product_line_1 = ProductLineFactory(product_id=product, display_order=None)
        product_line_2 = ProductLineFactory(product_id=product, display_order=None)
        product_line_3 = ProductLineFactory(product_id=product, display_order=5)
        product_line_4 = ProductLineFactory(product_id=product, display_order=None)

        assert product_line_1.display_order == 1
        assert product_line_2.display_order == 2
        assert product_line_3.display_order == 5
        assert product_line_4.display_order == 6

    def test_ordering_field_uniqueness(self):
        """Test uniqueness validation for OrderingField."""
        category = CategoryFactory()
        product_type = ProductTypeFactory()
        product = ProductFactory(category_id=category, product_type_id=product_type)
        ProductLineFactory(product_id=product, display_order=1)

        with pytest.raises(
            ValidationError, match="The display order .* is already in use."
        ):
            ProductLineFactory(product_id=product, display_order=1)
