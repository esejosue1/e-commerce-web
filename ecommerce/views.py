from django.shortcuts import render
from store.models import Product


# return home
def home(request):
    # only filtered the available products to the home page
    products = Product.objects.all().filter(is_available=True)
    # pass in only the products
    context = {
        'products': products,
    }
    # return the context products
    return render(request, 'home.html', context)
