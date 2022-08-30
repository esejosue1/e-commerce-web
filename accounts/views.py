from email.message import EmailMessage, Message
from http.client import REQUEST_ENTITY_TOO_LARGE
from typing import Type
import requests

from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import is_valid_path
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

# django email verification packages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from accounts.models import Account
from shoppingcart.views import get_session_id
from shoppingcart.models import CartItem, ShoppingCart
from .forms import RegistrationForm, UserForm, UserFormProfile
from .models import UserProfile
from orders.models import Order, OrderProduct

# Create your views here.


def register(request):

    # create user registration if request is POST, get the users input from the Registration Form
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        # check validation, get each inputed value, save it, create user success
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            user_name = email.split('@')[0]
            password = form.cleaned_data['password']
            phone_number = form.cleaned_data['phone_number']
            user = Account.objects.create_user(
                first_name=first_name, last_name=last_name, email=email, username=user_name, password=password)
            user.phone_number = phone_number
            user.save()
            
            #once the user is created, create a userProfile afterwards, default an image
            user_profile=UserProfile()
            user_profile.user_id=user.id
            
            user_profile.profile_picture="default/avatar2.png"
            user_profile.save()

            # USER Authentication
            current_site = get_current_site(request)
            mail_subject = 'Email Confirmation Required'
            message = render_to_string('account/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # django message if success, return redirect request
            #messages.success(request, 'Account has been created, please confirm verification in your email for account activation.')
            return redirect('/account/login?command=verification&email='+email)

    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'account/register.html', context)

# login user with email and password, authenticate, and log in


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)

        # if user successfully log in, check its cart content
        if user is not None:
            try:
                cart = ShoppingCart.objects.get(
                    cart_id=get_session_id(request))
                print(cart)
                cart_items_exist = CartItem.objects.filter(cart=cart).exists()
                print(cart_items_exist)
                if cart_items_exist:
                    print('entering ig')
                    cart_items = CartItem.objects.filter(cart=cart)

                    # getting product variation by cart id
                    product_variation = []
                    for item in cart_items:
                        p_variation = item.variation.all()
                        product_variation.append(list(p_variation))

                    # get the cart items from the user to access his product variation
                    cart_items = CartItem.objects.filter(user=user)
                    existing_variations_list = []
                    id = []

                    # get the item variation and its id
                    for item in cart_items:
                        existing_variation = item.variation.all()
                        existing_variations_list.append(
                            list(existing_variation))
                        id.append(item.id)

                    # check which variations match before and after login
                    for p in product_variation:
                        if p in existing_variations_list:
                            index = existing_variations_list.index(p)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_items = CartItem.objects.filter(cart=cart)
                            for item in cart_items:
                                item.user = user
                                item.save()

            except:
                pass

            auth.login(request, user)

            # with requests, get the whole previous url
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                # query -> next=/shoppingcart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                #{'next': '/shoppingcart/checkout/'}
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)

            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'No successful login')
            return redirect('login')

    return render(request, 'account/login.html')

# logs out the user, must be logged in


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'Successfully logged out')
    return redirect('login')


def verification(request, uidb64, token):

    # decode our token, check token, make user, otherwise no
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(Account.DoesNotExist, TypeError, ValueError, OverflowError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request, 'Validation Confirmed, you account has been created and active.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid verification, try again.')
        return redirect('register')


@login_required(login_url='login')
def dashboard(request):
    # get the total num of orders for dashboard display, -creared_at, the (-) gives results in descending order
    amount_of_orders = Order.objects.order_by(
        '-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders = amount_of_orders.count()
    user_profile=UserProfile.objects.get(user=request.user.id)
    context = {
        "orders": orders,
        "user_profile":user_profile,
    }
    return render(request, 'account/dashboard.html', context)

# if the user forget password


def forgotPassword(request):
    if request.method == 'POST':
        # check the user
        email = request.POST['email']  # get the name='email' in html file
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # reset password verification
            current_site = get_current_site(request)
            mail_subject = 'Password Reset'
            message = render_to_string('account/account_password_reset.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request,
                             'Reset password link have being mailed, verify email for account activation.')
            return redirect('login')

        else:
            messages.error(request, 'Email does not exist, try again.')
            return redirect('forgotPassword')
    return render(request, 'account/forgotPassword.html')

# verification format for password reset


def reset_password_verification(request, uidb64, token):
    # decode our token, check token, make user, otherwise no
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(Account.DoesNotExist, TypeError, ValueError, OverflowError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Password verification success.')
        return redirect('resetPassword')
    else:
        messages.error(request, 'Password link timed out, please try again.')
        return redirect('login')

# user reset password, confirm new passwords, update user's password in database


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(
                request, 'Password have being succesfully changed.')
            return redirect('login')
        else:
            messages.error(request,
                           "Password don't match, make sure to confirm password.")
            return redirect('resetPassword')
    else:
        return render(request, 'account/account_reset_password.html')

# get each users orders to showcase them in each myorders dashboard

@login_required(login_url='login')
def myOrders(request):
    my_orders = Order.objects.filter(
        user=request.user, is_ordered=True).order_by('-created_at')

    context = {
        "my_orders_dash": my_orders
    }

    return render(request, "account/myOrdersDashboard.html", context)

@login_required(login_url='login')
def editProfile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    # instance is to update the profile, not create
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        #update using form, request.FILES is used to update the image.jpg file
        user_profile = UserFormProfile(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and user_profile.is_valid():
            user_form.save()
            user_profile.save()
            messages.success(
                request, "Form completed, your information have been saved.")
            return redirect('editProfile')  
    #dont do anything, just show the users info
    else:
        user_form = UserForm(instance=request.user)
        user_profile = UserFormProfile(instance=profile)
    context = {
        'user_form': user_form,
        'user_profile': user_profile,
        'profile':profile,
    }
    return render(request, 'account/editProfile.html', context)


#sidebar option to change users profile password
@login_required(login_url='login')
def changePassword(request):
    if request.method=='POST':
        #get the data
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        
        #confirm the password, case sensative
        user=Account.objects.get(username__exact=request.user.username)
        
        #check for matches in pass
        if new_password == confirm_password:
            #check for current user
            success=user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password successfully changed!')
                return redirect('changePassword')
            else:
                messages.error(request, 'Current password did not match the user, try again.')
                return redirect('changePassword')
        else:
            messages.error(request, 'New passwords dont match!')
            return redirect('changePassword')
    return render(request, 'account/changePassword.html')


#show the details of orders when the user clicks on his/her order number
@login_required(login_url='login')
def orderDetail(request, order_id):
    #get the order num and order details
    order=Order.objects.get(order_number=order_id)
    order_details=OrderProduct.objects.filter(order__order_number=order_id)
    sub=order.order_total-order.tax
    context={
        'order':order,
        'order_details':order_details,
        'sub':sub
    }
    
    return render(request, 'account/orderDetail.html', context)