# creation of shopping cart url, will send the cart html once the request is made
from django.urls import path
from . import views

urlpatterns = [
    path('', views.shoppingcart, name='shoppingcart'),  #homepage for shopping cart window
    path('add_shoppingcart/<int:product_id>/',          #url path for when a product is added into the shopping cart
         views.add_shoppingcart, name='add_shoppingcart'), 
]
