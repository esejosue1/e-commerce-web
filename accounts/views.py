from email.message import EmailMessage, Message
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

        if user is not None:
            print(user)
            auth.login(request, user)
            return redirect('home')
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
