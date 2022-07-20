from django.shortcuts import render
from .models import Product
# Create your views here.


def store(request):
    # only filtered the available products to the home page
    products = Product.objects.all().filter(is_available=True)
    # pass in only the products
    product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count
    }
    return render(request, 'store/store.html', context)
