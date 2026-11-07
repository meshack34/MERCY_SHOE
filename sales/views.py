import json

from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_POST

from products.models import ProductVariant
from .models import Sale, SaleItem


@login_required
def pos(request):
    return render(request, 'sales/pos.html')


@login_required
@require_GET
def barcode_lookup(request):
    barcode = request.GET.get('barcode', '').strip()

    if not barcode:
        return JsonResponse({
            'success': False,
            'message': 'Please scan or enter a barcode.'
        }, status=400)

    try:
        variant = ProductVariant.objects.select_related(
            'product',
            'product__brand',
            'product__category'
        ).get(barcode=barcode)

    except ProductVariant.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Product not found. Check the barcode.'
        }, status=404)

    return JsonResponse({
        'success': True,
        'variant': {
            'id': variant.id,
            'barcode': variant.barcode,
            'product': variant.product.name,
            'brand': variant.product.brand.name,
            'size': str(variant.size),
            'colour': variant.colour,
            'price': str(variant.selling_price),
            'stock': variant.stock_quantity,
        }
    })


@login_required
@require_POST
def create_draft_sale(request):

    try:
        data = json.loads(request.body)

        cart_items = data.get('items', [])
        customer_name = data.get('customer_name', '').strip()
        customer_phone = data.get('customer_phone', '').strip()

        if not isinstance(cart_items, list) or not cart_items:
            return JsonResponse({
                'success': False,
                'message': 'Your shopping cart is empty.'
            }, status=400)

        # Combine repeated variants into one quantity.
        quantities = {}

        for item in cart_items:
            variant_id = int(item['variant_id'])
            quantity = int(item['quantity'])

            if quantity < 1:
                raise ValueError('Quantity must be at least 1.')

            quantities[variant_id] = (
                quantities.get(variant_id, 0) + quantity
            )

        with transaction.atomic():

            variants = ProductVariant.objects.select_for_update().filter(
                id__in=quantities.keys()
            ).select_related('product', 'product__brand')

            variants_by_id = {
                variant.id: variant for variant in variants
            }

            if len(variants_by_id) != len(quantities):
                return JsonResponse({
                    'success': False,
                    'message': 'One or more products could not be found.'
                }, status=400)

            # Validate stock before creating the draft.
            for variant_id, quantity in quantities.items():
                variant = variants_by_id[variant_id]

                if quantity > variant.stock_quantity:
                    return JsonResponse({
                        'success': False,
                        'message': (
                            f"Insufficient stock for "
                            f"{variant.product.name}, size {variant.size}. "
                            f"Available: {variant.stock_quantity}."
                        )
                    }, status=400)

            sale = Sale.objects.create(
                recorded_by=request.user,
                customer_name=customer_name,
                customer_phone=customer_phone,
                status='DRAFT',
                payment_status='PENDING',
            )

            total = Decimal('0.00')

            for variant_id, quantity in quantities.items():
                variant = variants_by_id[variant_id]

                item = SaleItem.objects.create(
                    sale=sale,
                    variant=variant,
                    quantity=quantity,
                    unit_price=variant.selling_price,
                )

                total += item.line_total

            sale.total_amount = total
            sale.save(update_fields=['total_amount'])

        return JsonResponse({
            'success': True,
            'message': 'Draft sale created successfully.',
            'sale_id': sale.id,
            'total': str(sale.total_amount),
            'redirect_url': f'/sales/{sale.id}/'
        })

    except (ValueError, TypeError, KeyError, InvalidOperation):
        return JsonResponse({
            'success': False,
            'message': 'Invalid sale information. Please check your cart.'
        }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid request data.'
        }, status=400)


@login_required
def sale_detail(request, sale_id):
    sale = get_object_or_404(
        Sale.objects.prefetch_related(
            'items__variant__product__brand'
        ),
        id=sale_id
    )

    return render(request, 'sales/sale_detail.html', {
        'sale': sale
    })