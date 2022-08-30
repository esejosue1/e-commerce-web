# creation of account url, will send anything related to acount login,register, and log out html
from django.urls import path
from . import views

urlpatterns = [
    # homepage for shopping cart window
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='dashboard'),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('verification/<uidb64>/<token>/',
         views.verification, name='verification'),
    path('reset_password_verification/<uidb64>/<token>/',
         views.reset_password_verification, name='reset_password_verification'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),
    path('myOrders/', views.myOrders, name='myOrders'),
    path('editProfile/', views.editProfile, name='editProfile'),
    path('changePassword/', views.changePassword, name='changePassword'),
    path('orderDetail/<int:order_id>/', views.orderDetail, name='orderDetail'),

]
