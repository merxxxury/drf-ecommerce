from django.contrib import admin

from .models import Product, Brand, Category, ProductLine, Attribute, AttributeValue


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
admin.site.register(ProductLine)
admin.site.register(Attribute)
admin.site.register(AttributeValue)


class ProductLineInline(admin.TabularInline):
    model = ProductLine


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductLineInline,
    ]
