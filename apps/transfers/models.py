from django.db import models
from apps.inventory.models import Warehouse, Product

class Transfer(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved (Stock Reserved)'),
        ('SHIPPED', 'Shipped (In Transit)'),
        ('RECEIVED', 'Received'),
        ('DISPUTED', 'Disputed (Discrepancy)'),
    ]
    source_warehouse = models.ForeignKey(Warehouse, related_name='transfers_out', on_delete=models.PROTECT)
    dest_warehouse = models.ForeignKey(Warehouse, related_name='transfers_in', on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    discrepancy_note = models.TextField(blank=True, help_text="JSON or text details of missing items")
    
    def __str__(self):
        return f"TR-{self.id} | {self.source_warehouse} -> {self.dest_warehouse}"

class TransferLine(models.Model):
    transfer = models.ForeignKey(Transfer, related_name='lines', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    # We might want to snapshot cost at time of transfer for accounting
    # unit_cost = models.DecimalField(...) 
    
    def __str__(self):
        return f"{self.product.sku} x {self.quantity}"
