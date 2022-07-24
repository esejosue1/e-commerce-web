
from django.urls import path
from . import views

urlpatterns = [

    path('', views.store, name="store"),
    # url path for products page
    path('<slug:category_slug>/', views.store, name="products_by_category"),
    # url path for each specific product
    path('<slug:category_slug>/<slug:product_slug>',
         views.product_detail, name="product_detail"),
]
