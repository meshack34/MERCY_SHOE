
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError

from .models import Brand, Category, Product, ProductVariant

from .forms import (
    BrandForm,
    CategoryForm,
    ProductForm,
    ProductVariantForm,
)

from .barcode_utils import generate_barcode_image


@login_required
def product_list(request):

    products = Product.objects.select_related(
        'brand',
        'category'
    ).prefetch_related('variants')

    search = request.GET.get('search', '').strip()

    if search:

        products = products.filter(
            name__icontains=search
        ) | products.filter(
            brand__name__icontains=search
        )

    context = {
        'products': products,
        'search': search,
    }

    return render(
        request,
        'products/product_list.html',
        context
    )


@login_required
def product_create(request):

    if request.method == 'POST':

        form = ProductForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            product = form.save()

            messages.success(
                request,
                'Product registered successfully.'
            )

            return redirect(
                'product_variant_create',
                product_id=product.id
            )

    else:

        form = ProductForm()

    return render(
        request,
        'products/product_form.html',
        {
            'form': form,
            'title': 'Register New Shoe',
        }
    )


@login_required
def product_edit(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if request.method == 'POST':

        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Product updated successfully.'
            )

            return redirect('product_list')

    else:

        form = ProductForm(instance=product)

    return render(
        request,
        'products/product_form.html',
        {
            'form': form,
            'title': 'Edit Product',
        }
    )


@login_required
def product_variant_create(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if request.method == 'POST':

        form = ProductVariantForm(request.POST)

        if form.is_valid():

            variant = form.save(commit=False)

            variant.product = product

            try:

                variant.save()

                generate_barcode_image(variant)

                messages.success(
                    request,
                    f'Variant created. Barcode: {variant.barcode}'
                )

                return redirect(
                    'product_variant_list',
                    product_id=product.id
                )

            except IntegrityError:

                form.add_error(
                    None,
                    'This shoe size and colour combination already exists.'
                )

    else:

        form = ProductVariantForm()

    return render(
        request,
        'products/variant_form.html',
        {
            'form': form,
            'product': product,
        }
    )


@login_required
def product_variant_list(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    variants = product.variants.all()

    return render(
        request,
        'products/variant_list.html',
        {
            'product': product,
            'variants': variants,
        }
    )


@login_required
def brand_list(request):

    brands = Brand.objects.all()

    return render(
        request,
        'products/brand_list.html',
        {'brands': brands}
    )


@login_required
def brand_create(request):

    if request.method == 'POST':

        form = BrandForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Brand created successfully.'
            )

            return redirect('brand_list')

    else:

        form = BrandForm()

    return render(
        request,
        'products/simple_form.html',
        {
            'form': form,
            'title': 'Add Brand',
        }
    )


@login_required
def category_list(request):

    categories = Category.objects.all()

    return render(
        request,
        'products/category_list.html',
        {'categories': categories}
    )


@login_required
def category_create(request):

    if request.method == 'POST':

        form = CategoryForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Category created successfully.'
            )

            return redirect('category_list')

    else:

        form = CategoryForm()

    return render(
        request,
        'products/simple_form.html',
        {
            'form': form,
            'title': 'Add Category',
        }
    )
