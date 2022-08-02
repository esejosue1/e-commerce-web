# what will be shown in the admin window
from django.contrib import admin
from .models import ShoppingCart, CartItem

# Register your models here.


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'date_added')


class ShoppingCartItem(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity', 'is_active')


# create two options in the admin page with cartItems and ShoppingCart
# FYI all categories must be done individually, NOT together
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(CartItem, ShoppingCartItem)
