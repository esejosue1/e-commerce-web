# what will be shown when a request is made, to the cart html file
from itertools import product

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from shoppingcart.models import CartItem, ShoppingCart
from store.models import Product, Variation
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
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
    variation_products = []
    current_user = request.user

    # if the user is authenticated, add its previous items in cart
    if current_user.is_authenticated:
        print('AUTHENTICATED')
        # check for POST request, including our product variations
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product,
                                                      variation_category__iexact=key, variation_value__iexact=value)
                    variation_products.append(variation)
                    print(variation)
                except:
                    pass

        # check if we have any cart items
        cart_item_exists = CartItem.objects.filter(
            product=product, user=current_user).exists()

        # if we do, get the cart items (cart_item)
        if cart_item_exists:
            cart_items = CartItem.objects.filter(
                product=product, user=current_user)
            existing_variations_list = []
            p_id = []

            # get the item variation and its id
            for item in cart_items:
                existing_variation = item.variation.all()
                existing_variations_list.append(list(existing_variation))
                p_id.append(item.id)

            # if the varion product model is in the existing var list, get its index, its id from that index, and get its info using product and id, increase quantity
            if variation_products in existing_variations_list:
                index = existing_variations_list.index(variation_products)
                item_id = p_id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            # no variation model exists in existing list, create one
            else:
                item = CartItem.objects.create(
                    product=product, quantity=1, user=current_user)
                # check what products we have in current shopping cart session, if we have variations, we include the variations to the product in the cart
                if len(variation_products) > 0:
                    item.variation.clear()
                    item.variation.add(*variation_products)
                item.save()

        # no product found in cart, create one
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user
            )
            if len(variation_products) > 0:
                cart_item.variation.clear()
                cart_item.variation.add(*variation_products)

            cart_item.save()
        # return HttpResponse(cart_item.quantity)
        # exit()
        return redirect('shoppingcart')  # redirect to shopping cart homwepage

    # user has not been authenticated, run with no login
    else:
        print('NOT AUTHENTICATED')

        # check for POST request, including our product variations
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product,
                                                      variation_category__iexact=key, variation_value__iexact=value)
                    variation_products.append(variation)
                    print(variation)
                except:
                    pass

        # want to check if we have a shopping cart session established
        try:
            cart = ShoppingCart.objects.get(
                cart_id=get_session_id(request))  # get the current session
        except ShoppingCart.DoesNotExist:  # else create and get new session
            cart = ShoppingCart.objects.create(
                cart_id=get_session_id(request)
            )
        cart.save()

        # check if we have any cart items
        cart_item_exists = CartItem.objects.filter(
            product=product, cart=cart).exists()

        # if we do, get the cart items (cart_item)
        if cart_item_exists:
            cart_items = CartItem.objects.filter(product=product, cart=cart)
            existing_variations_list = []
            p_id = []

            # get the item variation and its id
            for item in cart_items:
                existing_variation = item.variation.all()
                existing_variations_list.append(list(existing_variation))
                p_id.append(item.id)

            # if the varion product model is in the existing var list, get its index, its id from that index, and get its info using product and id, increase quantity
            if variation_products in existing_variations_list:
                index = existing_variations_list.index(variation_products)
                item_id = p_id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            # no variation model exists in existing list, create one
            else:
                item = CartItem.objects.create(
                    product=product, quantity=1, cart=cart)
                # check what products we have in current shopping cart session, if we have variations, we include the variations to the product in the cart
                if len(variation_products) > 0:
                    item.variation.clear()
                    item.variation.add(*variation_products)
                item.save()

        # no product found in cart, create one
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart
            )
            if len(variation_products) > 0:
                cart_item.variation.clear()
                cart_item.variation.add(*variation_products)

            cart_item.save()
        # return HttpResponse(cart_item.quantity)
        # exit()
        return redirect('shoppingcart')  # redirect to shopping cart homwepage

# remove products when decreasing quantity


def remove_shoppingcart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(
                product=product, user=request.user, id=cart_item_id)
        else:
            cart = ShoppingCart.objects.get(cart_id=get_session_id(request))
            cart_item = CartItem.objects.get(
                product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1  # decrease quantity
            cart_item.save()
        else:
            cart_item.delete()  # delete the product
    except:
        pass
    return redirect('shoppingcart')

# delete product item when user tabs delete button


def delete_shoppingcart(request, product_id, cart_item_id):

    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(
                product=product, id=cart_item_id, user=request.user)
            cart_item.delete()
        else:
            cart = ShoppingCart.objects.get(cart_id=get_session_id(request))
            cart_item = CartItem.objects.get(
                cart=cart, product=product, id=cart_item_id)
            cart_item.delete()

    except:
        pass

    return redirect('shoppingcart')


# what to show in the shopping cart view
def shoppingcart(request, total=0, quantity=0, cart_items=None):
    # check if we have a cart session, calculate total and quantity
    try:
        tax = 0
        grand_total = 0
        # if the user is already logged in, show previous items in cart that are active
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(
                user=request.user, is_active=True)
        # get a session id for that user
        else:
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

# in the checkout url, show in the right side box the products we have in cart


@login_required(login_url='login')
def checkout(request, total=0, quantity=0):
    # check if we have a cart session, calculate total and quantity
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(
                user=request.user, is_active=True)
        else:
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
    return render(request, 'store/checkout.html', context)
