
from decimal import Decimal

from django.db import models
from django.conf import settings
from django.utils import timezone

from suppliers.models import Supplier
from products.models import ProductVariant


class StockPurchase(models.Model):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='purchases'
    )

    invoice_number = models.CharField(
        max_length=100,
        blank=True
    )

    purchase_date = models.DateField(
        default=timezone.localdate
    )

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='stock_purchases'
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Purchase #{self.id} - {self.supplier.name}"

    @property
    def total_cost(self):
        return sum(
            (item.line_total for item in self.items.all()),
            Decimal('0.00')
        )

    class Meta:
        ordering = ['-purchase_date', '-created_at']


class StockPurchaseItem(models.Model):
    purchase = models.ForeignKey(
        StockPurchase,
        on_delete=models.PROTECT,
        related_name='items'
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name='purchase_items'
    )

    quantity = models.PositiveIntegerField()

    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    @property
    def line_total(self):
        return self.quantity * self.unit_cost

    def __str__(self):
        return f"{self.variant} - {self.quantity} pairs"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['purchase', 'variant'],
                name='unique_variant_per_purchase'
            )
        ]


class StockMovement(models.Model):

    MOVEMENT_TYPES = [
        ('PURCHASE', 'Purchase'),
        ('SALE', 'Sale'),
        ('RETURN', 'Customer Return'),
        ('DAMAGE', 'Damaged Stock'),
        ('ADJUSTMENT', 'Stock Adjustment'),
    ]

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name='stock_movements'
    )

    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPES
    )

    # Positive number increases stock.
    # Negative number reduces stock.
    quantity_change = models.IntegerField()

    reference = models.CharField(
        max_length=100,
        blank=True
    )

    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='stock_movements'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.variant} | "
            f"{self.movement_type} | "
            f"{self.quantity_change}"
        )

    class Meta:
        ordering = ['-created_at']
