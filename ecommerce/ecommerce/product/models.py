from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from .managers import IsActiveManager
from .fields import OrderingField

from django.core.exceptions import ValidationError


class Category(MPTTModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=250)
    is_active = models.BooleanField(default=False)
    parent = TreeForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='children',
    )

    # Managers
    objects = models.Manager()
    active = IsActiveManager()

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)

    # Managers
    objects = models.Manager()
    active = IsActiveManager()

    def __str__(self):
        return self.name


class ProductType(models.Model):
    type_name = models.CharField(max_length=150)
    attributes = models.ManyToManyField(
        "Attribute",
        through='ProductTypeAttribute',
        related_name='product_type_attribute',
    )

    def __str__(self):
        return str(self.type_name)


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250)
    description = models.TextField(blank=True)
    is_matcha = models.BooleanField(default=True)
    category_id = TreeForeignKey(
        'Category',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    brand_id = models.ForeignKey(Brand, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    product_type_id = models.ForeignKey(
        ProductType, on_delete=models.PROTECT, related_name='product'
    )

    # Managers
    objects = models.Manager()
    active = IsActiveManager()

    def __str__(self):
        return self.name


class Attribute(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)


class AttributeValue(models.Model):
    value = models.CharField(max_length=100)
    attribute_id = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.attribute_id.name}: {self.value}'


class ProductTypeAttribute(models.Model):
    product_type = models.ForeignKey(
        ProductType, on_delete=models.CASCADE, related_name='product_type_attribute_pt'
    )
    attribute = models.ForeignKey(
        Attribute, on_delete=models.CASCADE, related_name='product_type_attribute_a'
    )

    class Meta:
        unique_together = ('product_type', 'attribute')


class ProductLine(models.Model):
    price = models.DecimalField(max_digits=7, decimal_places=2)
    second_name = models.CharField(max_length=100, blank=True, default='')
    second_description = models.CharField(max_length=255, blank=True, default='')
    slug = models.SlugField(max_length=250)
    sku = models.CharField(max_length=250, unique=True, blank=True)
    quantity = models.IntegerField(default=1)
    # with related_name='product_line' is possible to refer to ProductLineSerializer via ProductSerializer
    product_id = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='product_line'
    )
    attributes = models.ManyToManyField(
        AttributeValue,
        blank=True,
        through='ProductLineAttributeValue',
        related_name='product_line_attribute_value',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    display_order = OrderingField(unique_for_field='product_id', blank=True, null=True)

    # Managers
    objects = models.Manager()
    active = IsActiveManager()

    def __str__(self):
        return f'{self.product_id.name} - {self.sku}'


class ProductLineAttributeValue(models.Model):
    product_line = models.ForeignKey(
        ProductLine,
        on_delete=models.CASCADE,
        related_name='product_attribute_value_pl',
    )
    attribute_value = models.ForeignKey(
        AttributeValue,
        on_delete=models.CASCADE,
        related_name='product_attribute_value_av',
    )

    class Meta:
        unique_together = (
            'product_line',
            'attribute_value',
        )

    def clean(self):
        # validate duplicates
        attribute_name = self.attribute_value.attribute_id.name
        if (
            ProductLineAttributeValue.objects.filter(
                product_line=self.product_line,
                attribute_value__attribute_id__name=attribute_name,
            )
            .exclude(id=self.id)
            .exists()
        ):
            raise ValidationError(
                f"The attribute '{attribute_name}' already exists for this product line."
            )

    def save(self, *args, **kwargs):
        # enforce validation before saving
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.attribute_value} {self.product_line}"


class ProductImage(models.Model):
    alternative_text = models.CharField(max_length=250, blank=True)
    url = models.ImageField(upload_to=None, default='test.jpg')
    product_line_id = models.ForeignKey(
        ProductLine, on_delete=models.CASCADE, related_name='product_image'
    )
    display_order = OrderingField(
        unique_for_field='product_line_id', blank=True, null=True
    )

    def __str__(self):
        return f'pl_{str(self.product_line_id.slug)}/order_{str(self.display_order)}'
