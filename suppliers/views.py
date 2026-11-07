from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Supplier
from .forms import SupplierForm


@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()

    search = request.GET.get('search', '')

    if search:
        suppliers = suppliers.filter(name__icontains=search)

    return render(request, 'suppliers/supplier_list.html', {
        'suppliers': suppliers,
        'search': search,
    })


@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier registered successfully.')
            return redirect('supplier_list')
    else:
        form = SupplierForm()

    return render(request, 'suppliers/supplier_form.html', {
        'form': form,
        'title': 'Register Supplier',
    })


@login_required
def supplier_edit(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)

    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)

        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated successfully.')
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)

    return render(request, 'suppliers/supplier_form.html', {
        'form': form,
        'title': 'Edit Supplier',
    })