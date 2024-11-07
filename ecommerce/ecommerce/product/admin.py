from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    Product,
    Brand,
    Category,
    ProductLine,
    Attribute,
    AttributeValue,
    ProductImage,
    ProductType,
)

from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet


class ProductLineAttributeValueInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        # use a set to track the unique attribute IDs
        attribute_ids = set()

        for form in self.forms:

            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                attribute_value = form.cleaned_data.get('attribute_value')
                if attribute_value.attribute_id:
                    if attribute_value.attribute_id in attribute_ids:
                        raise ValidationError(
                            f'Allowed only one unique attribute name per product line.'
                        )
                    attribute_ids.add(attribute_value.attribute_id)


class EditImageButton(object):
    def edit(self, instance):
        # Generate the URL to the ProductLineImage admin change list filtered by ProductLine
        url = reverse(
            f'admin:{instance._meta.app_label}_{instance._meta.model_name}_change',
            args=[instance.pk],
        )
        if instance.pk:
            link = mark_safe('<a href="{u}">edit</a>'.format(u=url))
            return link
        else:
            return ""

    edit.short_description = "Edit Images"


class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')  # Fields to display in the list view
    list_editable = ('is_active',)
    search_fields = ('name',)  # Add a search field for the name
    list_filter = ('is_active',)  # Add a filter for active/inactive brands


admin.site.register(Brand, BrandAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('name',)
    list_filter = ('is_active',)


admin.site.register(Category, CategoryAdmin)
# admin.site.register(AttributeValue)


class ProductLineImageInline(admin.TabularInline):
    model = ProductImage


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue.product_line_attribute_value.through
    formset = ProductLineAttributeValueInlineFormSet


class AttributeInline(admin.TabularInline):
    model = Attribute.product_type_attribute.through


class ProductLineAdmin(admin.ModelAdmin):
    inlines = [
        ProductLineImageInline,
        AttributeValueInline,
    ]


class ProductLineInline(EditImageButton, admin.TabularInline):
    model = ProductLine

    readonly_fields = ['edit']


class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductLineInline,
    ]


class ProductTypeAdmin(admin.ModelAdmin):
    inlines = [AttributeInline]


admin.site.register(ProductImage)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductLine, ProductLineAdmin)
admin.site.register(AttributeValue)
admin.site.register(Attribute)
admin.site.register(ProductType, ProductTypeAdmin)
