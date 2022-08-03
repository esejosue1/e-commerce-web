from django.shortcuts import redirect, render
from .forms import RegistrationForm
# Create your views here.


def register(request):
    form = RegistrationForm()
    context={
        'form': form,
    }
    return render(request, 'account/register.html', context)


def login(request):
    return render(request, 'account/login.html')


def logout(request):
    return
