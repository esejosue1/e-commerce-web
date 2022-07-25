# what will be shown in the admin window
from django.contrib import admin
from .models import ShoppingCart, CartItem

# Register your models here.
# create two options in the admin page with cartItems and ShoppingCart
# FYI all categories must be done individually, NOT together
admin.site.register(ShoppingCart)
admin.site.register(CartItem)
