# models use for the admin user to add data under the store category
from itertools import count, product
from django.db import models
from django.urls import reverse
from django.db.models import Avg, Count


from category.models import Category
from accounts.models import Account



# Create your models here.

# what the product model will have


class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, unique=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    # models.CASCADE= whenever the category gets deleted, the entire product gets deleted
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    # url path to direct to each product page through the products page, self(class product).category(//access the category under this class product)
    # .slug(//access the slug in the category section under slug, they are foreign keys)
    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name
    
    #get the avg of review rating of each product
    def reviewCalculator(self):
        review_of_product=ProductReview.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        average=0
        #since the above line have average inside, must initiate a new avg var with 0
        if review_of_product['average'] is not None:
            
            average+=float(review_of_product['average'])
            return average
        else:
            return average
    
    #get the total count of review for each product
    def reviewCount(self):
        totalReview=ProductReview.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        total=0
        if totalReview['count'] is not None:
            total+=int(totalReview['count'])
            return total
        else:
            return total

variation_category_choice = (
    ('color', 'color'),
    ('size', 'size'),
)

# modify the query set


class VariationManager(models.Manager):
    # return only the colors category under color and is_active
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)

    # return only the colors category under size and is_active
    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)


class Variation(models.Model):
    # if the product gets deleted, the variation should be deleted
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(
        max_length=100, choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    # run the manager for its size and color categories
    objects = VariationManager()

    def __str__(self):
        # return product value from Variation class, get a string variation value
        return self.variation_value

class ProductReview(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    user=models.ForeignKey(Account, on_delete=models.CASCADE)
    subject=models.CharField(max_length=100, blank=True)
    review=models.TextField(max_length=100, blank=True)
    rating=models.FloatField()
    ip=models.CharField(max_length=20,blank=True)
    status=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.subject