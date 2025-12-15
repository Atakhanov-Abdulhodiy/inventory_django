from django.contrib import admin
from apps.transfers.models import Transfer, TransferLine

class TransferLineInline(admin.TabularInline):
    model = TransferLine
    extra = 1

@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('id', 'source_warehouse', 'dest_warehouse', 'status', 'created_at')
    list_filter = ('status',)
    inlines = [TransferLineInline]
