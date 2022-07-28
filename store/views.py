from itertools import product
from tkinter import E

from django.shortcuts import get_object_or_404, render


from category.models import Category
from .models import Product
from category.models import Category
from shoppingcart.views import get_session_id, shoppingcart
from shoppingcart.models import CartItem


# Create your views here.


def store(request, category_slug=None):
    # empty var to determine each product urls
    categories = None
    products = None

    # if there exist a category with products, direct to the categories url
    if category_slug != None:
        # get the category under the Category
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(
            category=categories, is_available=True)  # filter throught the products for which are available and under the specific category
        product_count = products.count()  # count the total items under that category
    # else display nothing with a zero total count
    else:
        # only filtered the available products to the home page
        products = Product.objects.all().filter(is_available=True)
        # pass in only the products
        product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count
    }
    return render(request, 'store/store.html', context)

# What to show in the PRODUCT WINDOW, show the detail.html


def product_detail(request, category_slug, product_slug):
    # check if the product item been searched can be found in our category slug, else raise error
    try:
        single_product = Product.objects.get(
            category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=get_session_id(  # check in cartItems, filter throught the cart, obtaining the cart id (cart__cart_id) which will be the session id
            request), product=single_product).exists()  # if the item is in shopping cart already, return boolean

    except Exception as e:
        raise e

    # context will hold the single product to be used in the html doc as a reference
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
    }

    return render(request, 'store/product_detail.html', context)
