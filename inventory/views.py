
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.db import transaction
from django.db.models import F
from django.contrib import messages
from .models import StockPurchase, StockPurchaseItem, StockMovement
from .forms import StockPurchaseForm, StockPurchaseItemFormSet
from .models import StockMovement
from .forms import StockAdjustmentForm
from products.models import ProductVariant


@login_required
def purchase_list(request):

    purchases = StockPurchase.objects.select_related(
        'supplier',
        'recorded_by'
    ).prefetch_related(
        'items'
    )

    return render(
        request,
        'inventory/purchase_list.html',
        {
            'purchases': purchases,
        }
    )


@login_required
def purchase_create(request):

    if request.method == 'POST':

        purchase_form = StockPurchaseForm(request.POST)

        item_formset = StockPurchaseItemFormSet(request.POST)

        if purchase_form.is_valid() and item_formset.is_valid():

            items = [
                form.cleaned_data
                for form in item_formset
                if form.cleaned_data
            ]

            if not items:
                messages.error(
                    request,
                    'Please add at least one shoe variant.'
                )

            else:

                variant_ids = [
                    item['variant'].id
                    for item in items
                ]

                if len(variant_ids) != len(set(variant_ids)):

                    messages.error(
                        request,
                        'You have selected the same shoe variant more than once. '
                        'Combine its quantities into one row.'
                    )

                else:

                    try:
                        with transaction.atomic():

                            purchase = purchase_form.save(commit=False)

                            purchase.recorded_by = request.user

                            purchase.save()

                            for item in items:

                                variant = item['variant']

                                quantity = item['quantity']

                                unit_cost = item['unit_cost']

                                StockPurchaseItem.objects.create(
                                    purchase=purchase,
                                    variant=variant,
                                    quantity=quantity,
                                    unit_cost=unit_cost
                                )

                                # Increase the existing stock.
                                ProductVariant.objects.filter(
                                    id=variant.id
                                ).update(
                                    stock_quantity=F('stock_quantity') + quantity
                                )

                                # Record the stock movement.
                                StockMovement.objects.create(
                                    variant=variant,
                                    movement_type='PURCHASE',
                                    quantity_change=quantity,
                                    reference=f'Purchase #{purchase.id}',
                                    notes=f'Supplier: {purchase.supplier.name}',
                                    created_by=request.user
                                )

                        messages.success(
                            request,
                            'Stock purchase recorded and inventory updated successfully.'
                        )

                        return redirect(
                            'purchase_detail',
                            purchase_id=purchase.id
                        )

                    except Exception as error:

                        messages.error(
                            request,
                            f'Purchase could not be saved: {error}'
                        )

    else:

        purchase_form = StockPurchaseForm()

        item_formset = StockPurchaseItemFormSet()

    return render(
        request,
        'inventory/purchase_form.html',
        {
            'purchase_form': purchase_form,
            'item_formset': item_formset,
        }
    )


@login_required
def purchase_detail(request, purchase_id):

    purchase = get_object_or_404(
        StockPurchase.objects.select_related(
            'supplier',
            'recorded_by'
        ).prefetch_related(
            'items__variant__product__brand',
            'items__variant__product__category'
        ),
        id=purchase_id
    )

    return render(
        request,
        'inventory/purchase_detail.html',
        {
            'purchase': purchase,
        }
    )


@login_required
def inventory_dashboard(request):

    variants = ProductVariant.objects.select_related(
        'product',
        'product__brand',
        'product__category'
    ).order_by(
        'product__name',
        'size'
    )

    low_stock_variants = variants.filter(
        stock_quantity__lte=5
    )

    total_pairs = sum(
        variant.stock_quantity for variant in variants
    )

    context = {
        'variants': variants,
        'low_stock_variants': low_stock_variants,
        'total_variants': variants.count(),
        'total_pairs': total_pairs,
        'low_stock_count': low_stock_variants.count(),
    }

    return render(
        request,
        'inventory/inventory_dashboard.html',
        context
    )


@login_required
def stock_adjustment(request):

    if request.method == 'POST':

        form = StockAdjustmentForm(request.POST)

        if form.is_valid():

            variant = form.cleaned_data['variant']
            movement_type = form.cleaned_data['movement_type']
            quantity = form.cleaned_data['quantity']
            direction = form.cleaned_data['direction']
            notes = form.cleaned_data['notes']

            if movement_type == 'DAMAGE':
                quantity_change = -quantity

            elif movement_type == 'RETURN':
                quantity_change = quantity

            elif movement_type == 'ADJUSTMENT':
                quantity_change = (
                    quantity if direction == 'IN' else -quantity
                )

            try:
                with transaction.atomic():

                    locked_variant = ProductVariant.objects.select_for_update().get(
                        pk=variant.pk
                    )

                    new_stock = (
                        locked_variant.stock_quantity + quantity_change
                    )

                    if new_stock < 0:

                        form.add_error(
                            'quantity',
                            'You cannot reduce stock below zero. '
                            f'Available stock: {locked_variant.stock_quantity}.'
                        )

                    else:

                        locked_variant.stock_quantity = new_stock
                        locked_variant.save(
                            update_fields=['stock_quantity']
                        )

                        StockMovement.objects.create(
                            variant=locked_variant,
                            movement_type=movement_type,
                            quantity_change=quantity_change,
                            reference='Manual inventory adjustment',
                            notes=notes,
                            created_by=request.user
                        )

                        messages.success(
                            request,
                            'Inventory updated successfully.'
                        )

                        return redirect('inventory_dashboard')

            except ProductVariant.DoesNotExist:
                messages.error(
                    request,
                    'The selected shoe variant could not be found.'
                )

    else:
        form = StockAdjustmentForm()

    return render(
        request,
        'inventory/stock_adjustment.html',
        {'form': form}
    )


@login_required
def stock_movement_list(request):

    movements = StockMovement.objects.select_related(
        'variant',
        'variant__product',
        'variant__product__brand',
        'created_by'
    ).order_by('-created_at')

    return render(
        request,
        'inventory/stock_movements.html',
        {'movements': movements}
    )
