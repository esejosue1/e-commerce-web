#should return the dictionary of the data when you select the category options navbar

from os import link
from sre_constants import CATEGORY
from .models import Category

def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)