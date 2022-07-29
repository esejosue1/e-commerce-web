from .models import CartItem, ShoppingCart
from .views import get_session_id


def counter(request):
    cart_counter = 0
    if 'admin' in request.path:
        return ()
    else:
        try:
            cart = ShoppingCart.objects.filter(cart_id=get_session_id(request))
            cart_items = CartItem.objects.filter(cart=cart[:1])
            for cart_item in cart_items:
                cart_counter += cart_item.quantity
        except ShoppingCart.DoesNotExist:
            cart_counter = 0
    return dict(cart_counter=cart_counter)
