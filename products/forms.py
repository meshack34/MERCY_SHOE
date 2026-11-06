
from django import forms
from .models import Brand, Category, Product, ProductVariant


class BrandForm(forms.ModelForm):

    class Meta:
        model = Brand
        fields = ['name', 'description']


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ['name', 'description']


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product

        fields = [
            'brand',
            'category',
            'name',
            'description',
            'image',
        ]

        widgets = {
            'description': forms.Textarea(
                attrs={'rows': 3}
            ),
        }


class ProductVariantForm(forms.ModelForm):

    class Meta:
        model = ProductVariant

        fields = [
            'size',
            'colour',
            'buying_price',
            'selling_price',
            'stock_quantity',
        ]

        widgets = {
            'buying_price': forms.NumberInput(
                attrs={'step': '0.01', 'min': '0'}
            ),
            'selling_price': forms.NumberInput(
                attrs={'step': '0.01', 'min': '0'}
            ),
            'stock_quantity': forms.NumberInput(
                attrs={'min': '0'}
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        buying_price = cleaned_data.get('buying_price')
        selling_price = cleaned_data.get('selling_price')

        if (
            buying_price is not None
            and selling_price is not None
            and selling_price < buying_price
        ):
            self.add_error(
                'selling_price',
                'Selling price should not be below buying price.'
            )

        return cleaned_data
