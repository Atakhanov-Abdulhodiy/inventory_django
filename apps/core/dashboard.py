from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from apps.core.models import Product as CoreProduct, Customer as CoreCustomer, Invoice as CoreInvoice
from apps.inventory.models import Product, StockBatch, StockTransaction

def login_view(request):
    """Login page"""
    if request.user.is_authenticated:
        return redirect('home')
    
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error = "Invalid username or password"
    
    return render(request, 'login.html', {'error': error})

def logout_view(request):
    """Logout"""
    logout(request)
    return redirect('login')

@login_required(login_url='/login/')
def dashboard(request):
    """Main dashboard view with statistics"""
    stats = {
        'total_products': Product.objects.count(),
        'total_customers': CoreCustomer.objects.count(),
        'total_invoices': CoreInvoice.objects.count(),
        'total_batches': StockBatch.objects.count(),
    }
    
    recent_transactions = StockTransaction.objects.select_related(
        'batch__product'
    ).order_by('-timestamp')[:10]
    
    return render(request, 'dashboard.html', {
        'stats': stats,
        'recent_transactions': recent_transactions
    })
