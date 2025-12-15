from django.contrib import admin
from .models import Product, Warehouse, StockBatch, StockTransaction

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'costing_method')
    search_fields = ('sku', 'name')

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'is_active')

@admin.register(StockBatch)
class StockBatchAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'current_qty', 'unit_cost', 'received_date')
    list_filter = ('warehouse', 'product')

@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('batch', 'transaction_type', 'quantity', 'timestamp', 'reference_id')
    list_filter = ('transaction_type',)
