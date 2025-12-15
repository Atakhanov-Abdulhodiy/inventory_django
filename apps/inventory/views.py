from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.inventory.models import Product

@login_required(login_url='/login/')
def product_list(request):
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})
