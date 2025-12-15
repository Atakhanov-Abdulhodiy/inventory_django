from django.db import transaction
from apps.inventory.services import deduct_stock

def approve_invoice(invoice):
    """
    Approves a draft invoice, deducts stock, calculates COGS/Profit, and updates status.
    """
    if invoice.status != 'DRAFT':
        raise ValueError("Only DRAFT invoices can be approved.")
        
    with transaction.atomic():
        total_cogs = 0
        total_revenue = 0
        
        for line in invoice.lines.all():
            # Deduct Stock (FIFO/LIFO)
            # We use invoice ID as reference
            cogs = deduct_stock(
                product=line.product,
                warehouse=invoice.warehouse,
                quantity_needed=line.quantity,
                reference_id=f"INV-{invoice.id}"
            )
            total_cogs += cogs
            total_revenue += (line.quantity * line.unit_price)
            
        # Update Invoice
        invoice.status = 'ISSUED'
        invoice.profit_margin = total_revenue - total_cogs
        invoice.save()
        
        return invoice
