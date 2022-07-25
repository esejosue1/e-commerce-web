# what will be shown when a request is made, to the cart html file
from django.shortcuts import render

# Create your views here.


def shoppingcart(request):
    return render(request, 'store/shoppingcart.html')
