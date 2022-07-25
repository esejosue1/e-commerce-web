# what will be shown when a request is made, to the cart html file
from django.shortcuts import redirect, render
from shoppingcart.models import CartItem, ShoppingCart
from store.models import Product
# Create your views here.

# function to obtain the current scession (cookie) frmo browser


def get_session_id(request):
    cart = request.session.session_key  # obtain the current session
    if not cart:
        cart = request.session.create()  # if not, create a new one
    return cart

# function that will add products into the cart


def add_shoppingcart(request, product_id):
    # get the product id from Product class
    product = Product.objects.get(id=product_id)
    # want to check if we have a shopping cart session established
    try:
        cart = ShoppingCart.objects.get(
            cart_id=get_session_id(request))  # get the current session
    except ShoppingCart.DoesNotExist:  # else create and get new session
        cart = ShoppingCart.objects.create(
            cart_id=get_session_id(request)
        )
    cart.save()

    # check what products we have in current shopping cart session
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
    cart_item.save()
    return redirect('shoppingcart')  # redirect to shopping cart homwepage


def shoppingcart(request):
    return render(request, 'store/shoppingcart.html')
