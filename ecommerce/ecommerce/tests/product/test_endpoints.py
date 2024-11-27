import pytest
from django.urls import reverse
import json

# provides access to db
pytestmark = pytest.mark.django_db


class TestCategoryEndpoint:
    endpoint = reverse('category-list')
    # syntax <basename>-list or <basename>-detail (from router urls.py)

    def test_category_get(self, category_factory, api_client):
        # Arrange
        category_factory.create_batch(2, is_active=True)
        # Act
        response = api_client().get(self.endpoint)
        # Assert
        assert response.status_code == 200
        assert len(json.loads(response.content)) == 2


class TestProductEndpoint:
    endpoint = '/api/product/'

    def test_return_all_products(self, product_factory, api_client):
        # Arrange
        product_factory.create_batch(4, is_active=True)
        # Act
        response = api_client().get(self.endpoint)
        # Assert
        assert response.status_code == 200
        assert len(json.loads(response.content)) == 4

    def test_return_single_product_by_slug(self, product_factory, api_client):
        product = product_factory(slug='product-1', is_active=True)
        # response = api_client().get(
        #     reverse('product-detail', kwargs={'slug': product.slug})
        # )
        response = api_client().get(f'{self.endpoint}{product.slug}/')
        assert response.status_code == 200
        assert len(json.loads(response.content)) == 1
        assert response.data[0]['slug'] == product.slug
        assert response.data[0]['name'] == product.name

    def test_return_product_by_category_slug(
        self, category_factory, product_factory, api_client
    ):
        category = category_factory(slug='test_category', is_active=True)
        product_factory(category_id=category, is_active=True)
        product_factory(category_id=category, is_active=True)

        response = api_client().get(f'{self.endpoint}category/{category.slug}/')

        assert response.status_code == 200

        assert len(json.loads(response.content)) == 2
        assert response.data[0]['category_slug'] == category.slug
