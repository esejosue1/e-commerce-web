# creation of account url, will send anything related to acount login,register, and log out html
from django.urls import path
from . import views

urlpatterns = [
    # homepage for shopping cart window
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),

]