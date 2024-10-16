from pytest_factoryboy import register
from rest_framework.test import APIClient
import pytest

from .factories import (
    CategoryFactory,
    BrandFactory,
    ProductFactory,
    ProductLineFactory,
    AttributeFactory,
    AttributeValueFactory,
    ProductImageFactory,
)


register(CategoryFactory)
register(BrandFactory)
register(ProductFactory)
register(ProductLineFactory)  # fixture name: product_line_factory
register(AttributeFactory)
register(AttributeValueFactory)
register(ProductImageFactory)


@pytest.fixture
def api_client():
    return APIClient
