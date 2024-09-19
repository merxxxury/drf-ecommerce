import pytest
from django.urls import reverse
import json


pytestmark = pytest.mark.django_db
# provides access to db


class TestCategoryEndpoint:
    endpoint = reverse('category-list')
    # syntax <basename>-list or <basename>-detail (from router urls.py)

    def test_category_get(self, category_factory, api_client):

        # Arrange
        category_factory.create_batch(1)
        # Act
        response = api_client().get(self.endpoint)
        # Assert
        assert response.status_code == 200
        # print(response.content)
        assert len(json.loads(response.content)) == 1


class TestBrandEndpoint:
    endpoint = '/api/brand/'

    def test_brand_endpoint(self, brand_factory, api_client):
        # Arrange
        brand_factory.create_batch(1)
        # Act
        response = api_client().get(self.endpoint)
        # Assert
        assert response.status_code == 200
        # print(response.content)
        assert len(json.loads(response.content)) == 1


class TestProductEndpoint:
    endpoint = '/api/product/'

    def test_product_endpoint(self, product_factory, api_client):
        # Arrange
        product_factory.create_batch(4)
        # Act
        response = api_client().get(self.endpoint)
        # Assert
        assert response.status_code == 200
        # print(response.content)
        assert len(json.loads(response.content)) == 4
