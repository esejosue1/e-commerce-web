from email.message import EmailMessage, Message
from http.client import REQUEST_ENTITY_TOO_LARGE
from typing import Type
from django.http import HttpResponse
from django.shortcuts import redirect, render
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
from .forms import RegistrationForm
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
                        
                    #check which variations match before and after login
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
    return render(request, 'account/dashboard.html')

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
