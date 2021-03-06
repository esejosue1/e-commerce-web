from django.contrib import admin
from .models import Product  # importing the Product class


# Register your models here.

# class that will desplay the following for the user to input values
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock',
                    'category', 'modified_date', 'is_available')
    # tuple with only one item
    prepopulated_fields = {'slug': ('product_name',)}


admin.site.register(Product, ProductAdmin)
