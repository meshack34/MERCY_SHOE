
from django.contrib import admin

from .models import (
    StockPurchase,
    StockPurchaseItem,
    StockMovement
)


class StockPurchaseItemInline(admin.TabularInline):
    model = StockPurchaseItem
    extra = 0
    can_delete = False


@admin.register(StockPurchase)
class StockPurchaseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'supplier',
        'invoice_number',
        'purchase_date',
        'recorded_by',
    )

    search_fields = (
        'supplier__name',
        'invoice_number',
    )

    list_filter = ('purchase_date',)

    inlines = [StockPurchaseItemInline]

    readonly_fields = ('recorded_by',)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        'variant',
        'movement_type',
        'quantity_change',
        'reference',
        'created_by',
        'created_at',
    )

    list_filter = ('movement_type', 'created_at')

    search_fields = (
        'variant__barcode',
        'variant__product__name',
        'reference',
    )
