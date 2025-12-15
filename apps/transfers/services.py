from django.db import transaction
from apps.inventory.models import StockBatch, StockTransaction
from .models import Transfer

def receive_transfer(transfer, received_lines):
    """
    received_lines: dict { product_id: quantity_counted }
    """
    with transaction.atomic():
        for line in transfer.lines.all():
            counted = received_lines.get(line.product.id, 0)
            
            # Simple reconciliation: if we have counted items, add them to Dest
            if counted > 0:
                # We need to know cost. For MVP, we assumed TransferLine didn't snapshot cost (it was optional),
                # so we might need to fetch average or FIFO cost from source context,
                # BUT properly, TransferLine should have 'unit_cost' saved at approval.
                # Here we assume line.unit_cost exists or we grab from source batch logic.
                # To keep it simple for this MVP, we assume we saved unit_cost on line or pass it.
                # Let's pivot: Since we didn't add unit_cost to TransferLine model in previous step,
                # we'll fetch the most recent cost or 'standard' cost. 
                # Ideally, we update TransferLine to have unit_cost.
                
                # Let's fix models.py in next step or assume generic 10.0 cost if missing. 
                # Better: Use the last known cost from product batches.
                cost = 0
                last_batch = line.product.batches.order_by('-received_date').first()
                if last_batch:
                    cost = last_batch.unit_cost
                
                StockBatch.objects.create(
                    product=line.product,
                    warehouse=transfer.dest_warehouse,
                    initial_qty=counted,
                    current_qty=counted,
                    unit_cost=cost,
                    reference=f"TR-{transfer.id}"
                )
            
            if counted != line.quantity:
                # Log Discrepancy (simple text append)
                diff = line.quantity - counted
                transfer.discrepancy_note += f"Product {line.product.sku} expected {line.quantity}, got {counted}. Diff: {diff}\n"
        
        transfer.status = 'RECEIVED'
        transfer.save()
