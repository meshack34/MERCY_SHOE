
from django import forms
from django.forms import formset_factory

from .models import StockPurchase
from products.models import ProductVariant


class StockPurchaseForm(forms.ModelForm):

    class Meta:
        model = StockPurchase

        fields = [
            'supplier',
            'invoice_number',
            'purchase_date',
            'notes',
        ]

        widgets = {
            'purchase_date': forms.DateInput(
                attrs={'type': 'date'}
            ),

            'notes': forms.Textarea(
                attrs={'rows': 3}
            ),
        }


class StockPurchaseItemForm(forms.Form):

    variant = forms.ModelChoiceField(
        queryset=ProductVariant.objects.select_related(
            'product',
            'product__brand'
        ).order_by(
            'product__name',
            'size'
        ),

        empty_label='Select shoe variant'
    )

    quantity = forms.IntegerField(
        min_value=1
    )

    unit_cost = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0
    )


StockPurchaseItemFormSet = formset_factory(
    StockPurchaseItemForm,
    extra=3
)


from django import forms
from products.models import ProductVariant


class StockAdjustmentForm(forms.Form):

    MOVEMENT_CHOICES = [
        ('DAMAGE', 'Damaged Shoes'),
        ('RETURN', 'Customer Return'),
        ('ADJUSTMENT', 'Stock Count Correction'),
    ]

    DIRECTION_CHOICES = [
        ('IN', 'Increase Stock'),
        ('OUT', 'Reduce Stock'),
    ]

    variant = forms.ModelChoiceField(
        queryset=ProductVariant.objects.select_related(
            'product',
            'product__brand'
        ).order_by('product__name', 'size'),
        empty_label='Select shoe variant'
    )

    movement_type = forms.ChoiceField(
        choices=MOVEMENT_CHOICES
    )

    direction = forms.ChoiceField(
        choices=DIRECTION_CHOICES,
        required=False
    )

    quantity = forms.IntegerField(
        min_value=1
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3})
    )

    def clean(self):
        cleaned_data = super().clean()

        movement_type = cleaned_data.get('movement_type')
        direction = cleaned_data.get('direction')

        if movement_type == 'ADJUSTMENT' and not direction:
            self.add_error(
                'direction',
                'Select whether stock should increase or decrease.'
            )

        return cleaned_data
