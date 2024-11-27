from django.contrib import admin
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.safestring import mark_safe
from .forms import ProductLineAttributeValueFormSet, ProductLineAttributeValueForm


from .models import (
    Product,
    Category,
    ProductLine,
    Attribute,
    AttributeValue,
    ProductImage,
    ProductType,
)


class ProductLineAttributeValueInline(admin.TabularInline):
    model = AttributeValue.product_line_attribute_value.through
    form = ProductLineAttributeValueForm
    formset = ProductLineAttributeValueFormSet


class EditButton(object):
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

    edit.short_description = "Edit"


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('name',)
    list_filter = ('is_active',)


class ProductLineImageInline(admin.TabularInline):
    model = ProductImage


class AttributeInline(admin.TabularInline):
    model = Attribute.product_type_attribute.through


class ProductLineAdmin(admin.ModelAdmin):
    inlines = [
        ProductLineImageInline,
        ProductLineAttributeValueInline,
    ]


class ProductLineInline(EditButton, admin.TabularInline):
    model = ProductLine

    readonly_fields = ['edit']


class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductLineInline,
    ]


class ProductTypeAdmin(admin.ModelAdmin):
    inlines = [AttributeInline]


admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductImage)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductLine, ProductLineAdmin)
admin.site.register(AttributeValue)
admin.site.register(Attribute)
admin.site.register(ProductType, ProductTypeAdmin)
