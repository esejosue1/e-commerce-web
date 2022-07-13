from django.shortcuts import render
#return home
def home(request):
    return render(request, 'home.html')
