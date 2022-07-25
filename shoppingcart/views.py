from django.shortcuts import render

# Create your views here.


def shoppingcart(request):
    return render(request, 'store/shoppingcart.html')
