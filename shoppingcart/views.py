# what will be shown when a request is made, to the cart html file
from itertools import product
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from shoppingcart.models import CartItem, ShoppingCart
from store.models import Product
from django.core.exceptions import ObjectDoesNotExist
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
    color = request.GET['color']
    size = request.GET['size']
    return HttpResponse(color + ''+size)
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
    # return HttpResponse(cart_item.quantity)
    # exit()
    return redirect('shoppingcart')  # redirect to shopping cart homwepage

# remove products when decreasing quantity


def remove_shoppingcart(request, product_id):

    cart = ShoppingCart.objects.get(cart_id=get_session_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1  # decrease quantity
        cart_item.save()
    else:
        cart_item.delete()  # delete the product

    return redirect('shoppingcart')

# delete product item when user tabs delete button


def delete_shoppingcart(request, product_id):
    cart = ShoppingCart.objects.get(cart_id=get_session_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(cart=cart, product=product)
    cart_item.delete()

    return redirect('shoppingcart')


# what to show in the shopping cart view
def shoppingcart(request, total=0, quantity=0, cart_items=None):
    # check if we have a cart session, calculate total and quantity
    try:
        tax = 0
        grand_total = 0
        cart = ShoppingCart.objects.get(cart_id=get_session_id(request))
        cart_items = CartItem.objects.filter(is_active=True, cart=cart)
        for product_item in cart_items:
            total += (product_item.quantity*product_item.product.price)
            quantity += product_item.quantity
        tax = (2*total)/100

        grand_total = total + tax

    except ObjectDoesNotExist:
        pass  # ignore

    # context to be pass to the html
    context = {
        'quantity': quantity,
        'total': total,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    }
    return render(request, 'store/shoppingcart.html', context)
