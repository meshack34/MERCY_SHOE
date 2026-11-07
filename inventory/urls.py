
from django.urls import path
from . import views

urlpatterns = [

    # Inventory dashboard
    path(
        '',
        views.inventory_dashboard,
        name='inventory_dashboard'
    ),

    # Stock purchases
    path(
        'purchases/',
        views.purchase_list,
        name='purchase_list'
    ),

    path(
        'purchases/add/',
        views.purchase_create,
        name='purchase_create'
    ),

    path(
        'purchases/<int:purchase_id>/',
        views.purchase_detail,
        name='purchase_detail'
    ),

    # Stock adjustments
    path(
        'adjustment/',
        views.stock_adjustment,
        name='stock_adjustment'
    ),

    # Stock movement history
    path(
        'movements/',
        views.stock_movement_list,
        name='stock_movement_list'
    ),
]
