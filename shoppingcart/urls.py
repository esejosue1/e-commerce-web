# creation of shopping cart url, will send the cart html once the request is made
from django.urls import path
from . import views

urlpatterns = [
    path('', views.shoppingcart, name='shoppingcart'),
]
