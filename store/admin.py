from django.contrib import admin
from .models import Product, ProductReview, Variation  # importing the Product class


# Register your models here.

# class that will desplay the following for the user to input values
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock',
                    'category', 'modified_date', 'is_available')
    # tuple with only one item
    prepopulated_fields = {'slug': ('product_name',)}

#class to display the variation option under the admin page
class variationAdmin(admin.ModelAdmin):
    
    list_display = ('product', 'variation_category', 'variation_value', #what will be shown
                    'is_active', 'created_date')
    list_editable = ('is_active',)  #is active check box
    list_filter = ('product', 'variation_category', 'variation_value')  #right side box that filter through the products


# get access to he code in which the admin will add data
admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, variationAdmin)
admin.site.register(ProductReview)