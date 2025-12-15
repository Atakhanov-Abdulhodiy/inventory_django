from rest_framework import serializers
from .models import Invoice, InvoiceLine

class InvoiceLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLine
        fields = ['product', 'quantity', 'unit_price']

class InvoiceSerializer(serializers.ModelSerializer):
    lines = InvoiceLineSerializer(many=True)
    
    class Meta:
        model = Invoice
        fields = ['id', 'customer', 'warehouse', 'status', 'total_amount', 'lines', 'profit_margin', 'created_at']
        read_only_fields = ['total_amount', 'status', 'profit_margin', 'created_at']
    
    def create(self, validated_data):
        lines_data = validated_data.pop('lines')
        invoice = Invoice.objects.create(**validated_data)
        for line_data in lines_data:
            InvoiceLine.objects.create(invoice=invoice, **line_data)
        return invoice
