from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import HttpResponse

def generate_invoice_pdf(invoice):
    """
    Generates a PDF for the given invoice and returns it as an HttpResponse.
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, f"INVOICE #{invoice.id}")
    
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 70, f"Date: {invoice.created_at.strftime('%Y-%m-%d')}")
    p.drawString(50, height - 85, f"Customer: {invoice.customer.name}")
    p.drawString(50, height - 100, f"Email: {invoice.customer.email}")
    
    p.drawString(300, height - 70, f"Status: {invoice.get_status_display()}")
    p.drawString(300, height - 85, f"Warehouse: {invoice.warehouse.name}")
    
    # Table Header
    y = height - 140
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, "Item")
    p.drawString(250, y, "Quantity")
    p.drawString(350, y, "Unit Price")
    p.drawString(450, y, "Total")
    
    # Table Content
    y -= 20
    p.setFont("Helvetica", 10)
    
    for line in invoice.lines.all():
        line_total = line.quantity * line.unit_price
        
        p.drawString(50, y, f"{line.product.sku} - {line.product.name[:30]}")
        p.drawString(250, y, str(line.quantity))
        p.drawString(350, y, f"NOK {line.unit_price}")
        p.drawString(450, y, f"NOK {line_total}")
        y -= 20
        
        if y < 50: # Page break logic simplified
            p.showPage()
            y = height - 50
            
    # Total
    y -= 20
    p.line(50, y+15, 500, y+15)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(350, y, "GRAND TOTAL:")
    p.drawString(450, y, f"NOK {invoice.total_amount}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer
