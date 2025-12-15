from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, F
from django.utils import timezone
from apps.sales.models import Invoice
from apps.inventory.models import Product, StockBatch

class DashboardSalesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Monthly Revenue
        current_month = timezone.now().month
        
        monthly_revenue = Invoice.objects.filter(
            status='ISSUED', 
            created_at__month=current_month
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Top 5 Products by Qty Sold
        # (Simplified: querying InvoiceLines would be better, but for demo we just show a static or simple metric)
        
        return Response({
            "monthly_revenue": monthly_revenue,
            "period": timezone.now().strftime("%B %Y")
        })

class DashboardStockView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Low Stock Alert (Threshold < 10)
        low_stock = StockBatch.objects.values('product__sku', 'product__name')\
            .annotate(total_qty=Sum('current_qty'))\
            .filter(total_qty__lt=10)
            
        return Response({
            "low_stock_count": low_stock.count(),
            "low_stock_items": low_stock
        })
