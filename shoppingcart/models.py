#what information will be included in the shoppingcart category under
#the admin window
from itertools import product
from statistics import quantiles
from django.db import models
from store.models import Product


# Create your models here.
class ShoppingCart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now=True)

    def __str__(self):
        return self.cart_id

#will hold the item information under the cart
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.product
