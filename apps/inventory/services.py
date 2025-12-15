from django.db import transaction
from django.db.models import F
from .models import StockBatch, StockTransaction

def deduct_stock(product, warehouse, quantity_needed, reference_id):
    """
    Deducts stock from batches based on Product's costing method (FIFO/LIFO).
    Returns the total cost of goods sold (COGS) for this transaction.
    Raises ValueError if insufficient stock.
    """
    with transaction.atomic():
        # 1. Select batches with stock
        batches = product.batches.filter(warehouse=warehouse, current_qty__gt=0)
        
        # 2. Apply Ordering
        if product.costing_method == 'LIFO':
            batches = batches.order_by('-received_date')
        else: # FIFO and AVG (Flow is FIFO usually)
            batches = batches.order_by('received_date')
            
        remaining_qty = quantity_needed
        total_cogs = 0
        
        # Lock rows? In highly concurrent setting we might need select_for_update, 
        # but standard filter is okay for MVP unless specified otherwise.
        # batches = batches.select_for_update() 
        
        for batch in batches:
            if remaining_qty <= 0:
                break
                
            deduct_amount = min(batch.current_qty, remaining_qty)
            
            # Update specific batch
            batch.current_qty = F('current_qty') - deduct_amount
            batch.save()
            
            # Since F expressions delay value, we need to refresh to get actual if we needed it for logic,
            # but here we know what we deducted.
            # However, for COGS calc, we use the known unit_cost.
            
            # Calculate Cost
            total_cogs += deduct_amount * batch.unit_cost
            
            # Create Transaction Record
            StockTransaction.objects.create(
                batch=batch,
                transaction_type='SALE',
                quantity=-deduct_amount,
                reference_id=reference_id
            )
            
            remaining_qty -= deduct_amount
            
        if remaining_qty > 0:
            raise ValueError(f"Insufficient stock! Short by {remaining_qty}")
            
        return total_cogs

def add_stock(product, warehouse, quantity, unit_cost, reference_id):
    """
    Simple stock addition (Purchase).
    """
    batch = StockBatch.objects.create(
        product=product,
        warehouse=warehouse,
        initial_qty=quantity,
        current_qty=quantity,
        unit_cost=unit_cost,
        reference=reference_id
    )
    
    StockTransaction.objects.create(
        batch=batch,
        transaction_type='PURCHASE',
        quantity=quantity,
        reference_id=reference_id
    )
    return batch
