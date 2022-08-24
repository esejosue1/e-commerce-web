from itertools import product
from tkinter import E
from django.http import HttpResponse
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib import messages, auth


from category.models import Category
from orders.models import OrderProduct
from .forms import ReviewForm
from .models import Product, ProductReview
from category.models import Category
from shoppingcart.views import get_session_id, shoppingcart
from shoppingcart.models import CartItem


# Create your views here.


def store(request, category_slug=None):
    # empty var to determine each product urls
    categories = None
    products = None

    # if there exist a category with products, direct to the categories url
    if category_slug != None:
        # get the category under the Category
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(
            category=categories, is_available=True)  # filter throught the products for which are available and under the specific category
        product_count = products.count()  # count the total items under that category
        paginator = Paginator(products, 3)
        page = request.GET.get('page')  # get the page number
        paged_products = paginator.get_page(
            page)  # store the num of products/page

    # else display nothing with a zero total count
    else:
        # only filtered the available products to the home page
        products = Product.objects.all().filter(is_available=True).order_by('id')

        # number of products to be listed per page num
        paginator = Paginator(products, 3)
        page = request.GET.get('page')  # get the page number
        paged_products = paginator.get_page(
            page)  # store the num of products/page
        # pass in only the products
        product_count = products.count()
    context = {
        'products': paged_products,
        'product_count': product_count
    }
    return render(request, 'store/store.html', context)

# What to show in the PRODUCT WINDOW, show the detail.html


def product_detail(request, category_slug, product_slug):
    # check if the product item been searched can be found in our category slug, else raise error
    try:
        single_product = Product.objects.get(
            category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=get_session_id(  # check in cartItems, filter throught the cart, obtaining the cart id (cart__cart_id) which will be the session id
            request), product=single_product).exists()  # if the item is in shopping cart already, return boolean

    except Exception as e:
        raise e

    #check if the user have purchase the product in order to submit review
    try:
        purchased_product=OrderProduct.objects.filter(user=request.user, product=single_product.id).exist()
    except:
        purchased_product=None
    
    #get the reviews of each product to showcase them 
    reviews=ProductReview.objects.filter(product=single_product.id, status=True)
    
    # context will hold the single product to be used in the html doc as a reference
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'purchased_product':purchased_product,
        'reviews':reviews,
    }

    return render(request, 'store/product_detail.html', context)


def search(request):
    # if the keyword exist, get its value ['keyword]
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            # look for the whole description that matches the keyword
            products = Product.objects.order_by(
                '-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            found = products.count()
    context = {
        'products': products,
        'product_count': found,
    }
    return render(request, 'store/store.html', context)


def productReview(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        # check for existing review, update
        try:
            reviews = ProductReview.objects.get(
                user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Your review have been updated.')
            return redirect(url)
        # create a new review post for the user
        except ProductReview.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ProductReview()
                data.product_id = product_id
                data.user_id = request.user.id
                data.subject = form.cleaned_data['subject']
                data.review = form.cleaned_data['review']
                data.rating = form.cleaned_data['rating']
                data.ip = request.META.get('REMOTE_ADDR')
                data.save()
                messages.success(
                    request, "Your review have been successfully submitted.")
                return redirect(url)
