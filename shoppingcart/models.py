# what information will be included in the shoppingcart category under
# the admin window
from itertools import product
from statistics import quantiles
from django.db import models
from store.models import Product, Variation
from accounts.models import Account


# Create your models here.
class ShoppingCart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now=True)

    def __str__(self):
        return self.cart_id

# will hold the item information under the cart


class CartItem(models.Model):
    user=models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE, null=True)
    # manytomanyfield is for a product to have other variations for the same prsoduct
    variation = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    # show current total of specific product items
    def subtotal(self):
        return self.product.price*self.quantity

    def __unicode__(self):
        return self.product
