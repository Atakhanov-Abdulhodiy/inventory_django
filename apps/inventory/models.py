from django.db import models
from django.utils import timezone

class Product(models.Model):
    COSTING_CHOICES = [
        ('FIFO', 'First-In First-Out'),
        ('LIFO', 'Last-In First-Out'),
        ('AVG', 'Weighted Average'),
    ]
    sku = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    costing_method = models.CharField(max_length=4, choices=COSTING_CHOICES, default='FIFO')
    description = models.TextField(blank=True)
    
    # Dimensions for Cube Calc
    length = models.FloatField(default=0, help_text="cm")
    width = models.FloatField(default=0, help_text="cm")
    height = models.FloatField(default=0, help_text="cm")
    
    def __str__(self):
        return f"{self.sku} - {self.name}"

class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class StockBatch(models.Model):
    """
    Represents a specific batch of inventory received at a specific cost.
    Crucial for FIFO/LIFO calculations.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='batches')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='batches')
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    initial_qty = models.IntegerField()
    current_qty = models.IntegerField()
    received_date = models.DateTimeField(default=timezone.now)
    reference = models.CharField(max_length=100, blank=True, help_text="PO Number or Transfer ID")
    
    class Meta:
        ordering = ['received_date'] # Default FIFO
        verbose_name_plural = "Stock Batches"
        indexes = [
            models.Index(fields=['product', 'warehouse', 'current_qty']),
        ]

    def __str__(self):
        return f"{self.product.sku} | Qty: {self.current_qty} | Cost: {self.unit_cost}"

class StockTransaction(models.Model):
    TX_TYPES = [
        ('PURCHASE', 'Purchase In'),
        ('SALE', 'Sale Out'),
        ('RETURN', 'Customer Return'),
        ('ADJUST', 'Inventory Adjustment'),
        ('TRANSFER_OUT', 'Transfer Out'),
        ('TRANSFER_IN', 'Transfer In'),
    ]
    batch = models.ForeignKey(StockBatch, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TX_TYPES)
    quantity = models.IntegerField(help_text="Negative for outflow, Positive for inflow")
    reference_id = models.CharField(max_length=100, blank=True) # e.g. Invoice ID
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_type} | {self.quantity} | {self.timestamp}"
