# creation of shopping cart url, will send the cart html once the request is made
from django.urls import path
from . import views

urlpatterns = [
    # homepage for shopping cart window
    path('', views.shoppingcart, name='shoppingcart'),
    path('add_shoppingcart/<int:product_id>/',  # url path for when a product is added into the shopping cart
         views.add_shoppingcart, name='add_shoppingcart'),
    path('remove_shoppingcart/<int:product_id>/<int:cart_item_id>/',  # url path for when a product is remove from the shopping cart
         views.remove_shoppingcart, name='remove_shoppingcart'),
    path('delete_shoppingcart/<int:product_id>/<int:cart_item_id>/',  # url path for when a product is deleted from the shopping cart
         views.delete_shoppingcart, name='delete_shoppingcart'),
]
