from typing import List
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.

# creating an account


class MyAccountManager(BaseUserManager):

    # creating a user for our admin
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('Email is missing, user must have email')
        if not username:
            raise ValueError('Username missing')
        user = self.model(
            email=self.normalize_email(email),  # lower case email
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    # creating a super user once the user have been created
    def create_superuser(self, first_name, last_name, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=50)

    # requiered mandatory when creating a custom user model
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    # what the user must input
    # must have all of the requiered field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    # if the user is the admin, he can make changes
    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True

class UserProfile(models.Model):
    user=models.OneToOneField(Account, on_delete=models.CASCADE) #have only one profile for one user, more secure and unique
    address_1=models.CharField(blank=True, max_length=100)
    address_2=models.CharField(blank=True, max_length=100)
    profile_picture=models.ImageField(blank=True, upload_to='userprofile')
    city=models.CharField(blank=True, max_length=30)
    state=models.CharField(blank=True, max_length=30)
    country=models.CharField(blank=True, max_length=30)
    
    def __str__(self):
        return self.user.first_name
    
    def complete_addi(self):
        return f'{self.address_1} {self.address_2}'