from datetime import datetime
from urllib import request
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
import datetime

from shoppingcart.models import CartItem
from .forms import OrderForm
from .models import Order


# Create your views here.
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
            print('VALID')
            data = Order()
            data.user = user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.phone = form.cleaned_data['phone']
            data.address = form.cleaned_data['address']
            data.address2 = form.cleaned_data['address2']
            data.city = form.cleaned_data['city']
            data.state = form.cleaned_data['state']

            # total order
            data.total = grand_total
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
            return redirect('checkout')
        else:
            print(form.errors)
            return redirect('checkout')
