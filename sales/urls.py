from django.urls import path
from . import views

urlpatterns = [
    path('', views.pos, name='pos'),
    path('barcode-lookup/', views.barcode_lookup, name='barcode_lookup'),
    path('create-draft/', views.create_draft_sale, name='create_draft_sale'),
    path('<int:sale_id>/', views.sale_detail, name='sale_detail'),
]