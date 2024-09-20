from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    name = models.CharField(max_length=100, unique=True)
    parent = TreeForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='children',
    )

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_matcha = models.BooleanField(default=True)
    category_id = TreeForeignKey(
        'Category',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    brand_id = models.ForeignKey(Brand, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Attribute(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    value = models.CharField(max_length=100)
    attribute_id = models.ForeignKey(Attribute, on_delete=models.CASCADE)

    def __str__(self):
        return self.value


class ProductLine(models.Model):
    price = models.DecimalField(max_digits=7, decimal_places=2)
    sku = models.CharField(max_length=250, unique=True, blank=True)
    quantity = models.IntegerField(default=1)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    attributes = models.ManyToManyField(AttributeValue)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_id.name


class ProductImage(models.Model):
    name = models.CharField(max_length=250, blank=True)
    alternative_text = models.CharField(max_length=250, blank=True)
    location = models.URLField()
    product_line_id = models.ForeignKey(ProductLine, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}-{str(self.product_line_id)}'
