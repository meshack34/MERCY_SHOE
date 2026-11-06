
from django.contrib import admin
from .models import Brand, Category, Product, ProductVariant


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):

    list_display = ('name', 'created_at')

    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = ('name', 'created_at')

    search_fields = ('name',)


class ProductVariantInline(admin.TabularInline):

    model = ProductVariant

    extra = 1

    readonly_fields = ('barcode', 'barcode_image')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'brand',
        'category',
        'created_at',
    )

    list_filter = ('brand', 'category')

    search_fields = (
        'name',
        'brand__name',
    )

    inlines = [ProductVariantInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):

    list_display = (
        'product',
        'size',
        'colour',
        'buying_price',
        'selling_price',
        'stock_quantity',
        'barcode',
    )

    list_filter = ('size', 'colour')

    search_fields = (
        'product__name',
        'barcode',
    )

    readonly_fields = ('barcode', 'barcode_image')
