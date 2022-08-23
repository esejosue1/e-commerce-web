from datetime import datetime
from email import message
from email.errors import MessageError
from urllib import request
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib import messages


from shoppingcart.models import CartItem
from store.models import Product
from .forms import OrderForm
from .models import Order, Payment, OrderProduct

import datetime
import json


# Create your views here.

def payment(request):
    body = json.loads(request.body)
    print(body)
    order = Order.objects.get(
        user=request.user, is_ordered=False, order_number=body['orderID'])

    # store transaction details inside payment model
    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,  # accessed by the order query, total in models
        status=body['status'],
    )
    payment.save()

    # update and is_ordered in Order model since its a foreign key of Payment model
    order.payment = payment
    order.is_ordered = True
    order.save()

    print(body)

    # move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.payment = payment
        order_product.user_id = request.user.id
        order_product.product_id = item.product.id
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.is_ordered = True
        order_product.save()

        # get the variations of the cart item since we have manytomany variations
        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variation.all()
        order_product = OrderProduct.objects.get(id=order_product.id)
        order_product.variation.set(product_variation)
        order_product.save()

        # reduce the quantity of the sold prodcuts
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # clear cart
    CartItem.objects.filter(user=request.user).delete()

    # send order received email to customer
    mail_subject = 'Order Confirmation'
    message = render_to_string('orders/order_received_email.html', {
        'user': request.user,
        'order': order,

    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }

    # send back the data from where it came by, sendData() in html
    return JsonResponse(data)
    # return render(request, 'orders/payment.html')


# Grab the user info an save it into memmory to process payment and shipping
def place_order(request, total=0, quantity=0):
    # check if we have any items
    user = request.user
    cart_items = CartItem.objects.filter(user=user)
    amount_items = cart_items.count()
    if amount_items <= 0:
        return redirect('store')

    for item in cart_items:
        total += (item.product.price * item.quantity)
        quantity += item.quantity

    tax = (2*total)/100
    grand_total = total+tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        # store all the billing info inside the order table
        if form.is_valid():
            data = Order()
            data.user = user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.phone = form.cleaned_data['phone']
            data.address = form.cleaned_data['address']
            data.address2 = form.cleaned_data['address2']
            data.country = form.cleaned_data['country']
            data.city = form.cleaned_data['city']
            data.state = form.cleaned_data['state']
            data.order_note = form.cleaned_data['order_note']
            # total order
            data.order_total = grand_total
            data.tax = tax

            data.ip = request.META.get('REMOTE_ADDR')

            data.save()  # generates unique id

            # order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            o_number = current_date + str(data.id)
            data.order_number = o_number
            data.save()

            # grab the info from the Orders that matches user, havent been ordered yet, and match in order numbers
            order = Order.objects.get(
                user=user, is_ordered=False, order_number=o_number)

            # values to be access from the html
            context = {
                'order': order,
                'total': total,
                "tax": tax,
                'grand_total': grand_total,
                'cart_items': cart_items,
            }

            return render(request, 'orders/payment.html', context)
        else:
            print(form.errors)
            return redirect('checkout')

#what to pass once the order have been payed, get the order num and transID and pass them to the order-complete.html
def order_complete(request):
    order_number=request.GET.get("order_number")
    transID=request.GET.get("payment_id")
    
    #check if we have an order or payment successful
    try:
        order=Order.objects.get(order_number=order_number, is_ordered=True)
        items=OrderProduct.objects.filter(order_id=order.id)
        payment=Payment.objects.get(payment_id=transID)
        sub=order.order_total-order.tax
        context={
            'order':order,
            'items':items,
            'transID':payment.payment_id,
            'payment':payment,
            'sub':sub,
        }
        return render(request, 'orders/order_complete.html', context)
    except(Payment.DoesNotExist, Order.DoesNotExist):
        messages.error(request,"Order incomplete or Payment invalid, try again.")
        return redirect('home')
