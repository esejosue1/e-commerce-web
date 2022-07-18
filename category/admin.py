from django.contrib import admin
from .models import Category


# Register your models here.

# category that will fill in the slug at the same time when you put a new category
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'slug')


# import the categoryAdmin class
admin.site.register(Category, CategoryAdmin)
