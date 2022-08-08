from django.shortcuts import redirect, render
from django.urls import is_valid_path
from django.contrib import messages

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
            messages.success(request, 'Registration Successful')
            return redirect('register')
            

    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'account/register.html', context)


def login(request):
    return render(request, 'account/login.html')


def logout(request):
    return
