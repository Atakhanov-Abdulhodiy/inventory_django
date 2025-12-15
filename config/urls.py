from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from apps.sales.views import InvoiceViewSet
from apps.reports.views import DashboardSalesView, DashboardStockView
from apps.core.dashboard import dashboard, login_view, logout_view

# DRF Router
router = routers.DefaultRouter()
router.register(r'invoices', InvoiceViewSet)

urlpatterns = [
    # Authentication
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Home/Dashboard
    path('', dashboard, name='home'),
    
    path('admin/', admin.site.urls),
    
    # API Routes
    path('api/', include(router.urls)),
    path('api/dashboard/sales/', DashboardSalesView.as_view(), name='dashboard-sales'),
    path('api/dashboard/stock/', DashboardStockView.as_view(), name='dashboard-stock'),
    
    # Inventory Routes (replaces core)
    path('inventory/', include('apps.inventory.urls')),
    
    # Auth (Login/Logout for browsable API)
    path('api-auth/', include('rest_framework.urls')),
]
