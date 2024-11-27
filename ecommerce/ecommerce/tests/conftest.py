from pytest_factoryboy import register
from rest_framework.test import APIClient
import pytest

from .factories import (
    CategoryFactory,
    ProductFactory,
    ProductLineFactory,
    ProductImageFactory,
    ProductTypeFactory,
    AttributeFactory,
    AttributeValueFactory,
)


@pytest.fixture
def api_client():
    return APIClient


register(CategoryFactory)
register(ProductFactory)
register(ProductLineFactory)  # fixture name: product_line_factory
register(ProductImageFactory)
register(ProductTypeFactory)
register(AttributeFactory)
register(AttributeValueFactory)
