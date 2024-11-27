from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from .managers import IsActiveManager
from .fields import OrderingField

from django.core.exceptions import ValidationError


class Category(MPTTModel):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
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


class ProductType(models.Model):
    type_name = models.CharField(max_length=150)
    parent = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)
    attributes = models.ManyToManyField(
        "Attribute",
        through='ProductTypeAttribute',
        related_name='product_type_attribute',
    )

    def __str__(self):
        return str(self.type_name)


class Product(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    pid = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    is_digital = models.BooleanField(default=False)
    category_id = TreeForeignKey(
        'Category',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    is_active = models.BooleanField(default=False)
    product_type_id = models.ForeignKey(
        ProductType, on_delete=models.PROTECT, related_name='product_type'
    )
    attribute_values = models.ManyToManyField(
        'AttributeValue',
        through='ProductAttributeValue',
        related_name='product_attribute_value',
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    # Managers
    objects = models.Manager()
    active = IsActiveManager()

    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_attribute_value_p',
    )
    attribute_value = models.ForeignKey(
        'AttributeValue',
        on_delete=models.CASCADE,
        related_name='product_attribute_value_av',
    )

    class Meta:
        unique_together = (
            'product',
            'attribute_value',
        )


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
        unique_together = (
            'product_type',
            'attribute',
        )


class ProductLine(models.Model):
    display_order = OrderingField(unique_for_field='product_id', blank=True, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    slug = models.SlugField(max_length=250, unique=True)
    is_active = models.BooleanField(default=False)
    second_name = models.CharField(max_length=200, blank=True, default='')
    second_description = models.CharField(max_length=255, blank=True, default='')
    sku = models.CharField(max_length=250, unique=True, blank=True)
    quantity = models.IntegerField(default=1)
    weight = models.DecimalField(
        max_digits=7, decimal_places=3, default=Decimal('0.000'), null=True, blank=True
    )
    # with related_name='product_line' is possible to refer to ProductLineSerializer via ProductSerializer
    product_type_id = models.ForeignKey(
        ProductType, on_delete=models.PROTECT, related_name='product_line_type'
    )
    product_id = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='product_line'
    )
    attributes = models.ManyToManyField(
        AttributeValue,
        blank=True,
        through='ProductLineAttributeValue',
        related_name='product_line_attribute_value',
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    # Managers
    objects = models.Manager()
    active = IsActiveManager()

    def __str__(self):
        return f'{self.product_id.name} - {self.sku}'

    def _round_half_up(self, value, decimal_place):
        exp = Decimal(f"1.{'0' * decimal_place}")
        return Decimal(value).quantize(
            exp=exp,
            rounding=ROUND_HALF_UP,
        )

    def save(self, *args, **kwargs):
        if self.price is not None:
            self.price = self._round_half_up(self.price, decimal_place=2)
        if self.weight is not None:
            self.weight = self._round_half_up(self.weight, decimal_place=3)

        super().save(*args, **kwargs)


class ProductLineAttributeValue(models.Model):
    product_line = models.ForeignKey(
        ProductLine,
        on_delete=models.CASCADE,
        related_name='product_line_attribute_value_pl',
    )
    attribute_value = models.ForeignKey(
        AttributeValue,
        on_delete=models.CASCADE,
        related_name='product_line_attribute_value_av',
    )

    class Meta:
        unique_together = (
            'product_line',
            'attribute_value',
        )

    def clean(self):
        product_type = self.product_line.product_type_id
        allowed_attributes = product_type.attributes.values_list('name', flat=True)
        if getattr(self, 'attribute_value', None):
            # validate only allowed by product type attributes
            attribute_name = self.attribute_value.attribute_id.name

            if attribute_name not in allowed_attributes:
                raise ValidationError(
                    f"The attribute '{attribute_name}' is not allowed for product lines of type '{product_type}'."
                )

            # validate duplicates
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
        return f"{self.attribute_value}, {self.product_line}"


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
