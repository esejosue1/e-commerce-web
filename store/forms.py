from socket import fromshare
from django import forms
from .models import ProductReview

# form in which the user rates the product by stars and description


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['subject', 'review', 'rating']