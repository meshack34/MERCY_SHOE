
from django.urls import path
from . import views


urlpatterns = [

    path(
        '',
        views.product_list,
        name='product_list'
    ),

    path(
        'add/',
        views.product_create,
        name='product_create'
    ),

    path(
        '<int:product_id>/edit/',
        views.product_edit,
        name='product_edit'
    ),

    path(
        '<int:product_id>/variants/add/',
        views.product_variant_create,
        name='product_variant_create'
    ),

    path(
        '<int:product_id>/variants/',
        views.product_variant_list,
        name='product_variant_list'
    ),

    path(
        'brands/',
        views.brand_list,
        name='brand_list'
    ),

    path(
        'brands/add/',
        views.brand_create,
        name='brand_create'
    ),

    path(
        'categories/',
        views.category_list,
        name='category_list'
    ),

    path(
        'categories/add/',
        views.category_create,
        name='category_create'
    ),

]
