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
)


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
admin.site.register(Attribute)
admin.site.register(AttributeValue)


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


class ProductLineImageInline(admin.TabularInline):
    model = ProductImage


@admin.register(ProductLine)
class ProductLineAdmin(admin.ModelAdmin):
    inlines = [
        ProductLineImageInline,
    ]


class ProductLineInline(EditImageButton, admin.TabularInline):
    model = ProductLine
    readonly_fields = ['edit']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductLineInline,
    ]


admin.site.register(ProductImage)
