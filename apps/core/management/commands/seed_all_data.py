from django.core.management.base import BaseCommand
from apps.core.models import Product as CoreProduct, Customer as CoreCustomer, Invoice as CoreInvoice
from apps.inventory.models import Product, Warehouse, StockBatch, StockTransaction
from apps.sales.models import Customer, Invoice, InvoiceLine, Payment
from apps.transfers.models import Transfer, TransferLine
from apps.users.models import UserProfile
from faker import Faker
import random
from decimal import Decimal
from django.utils import timezone

class Command(BaseCommand):
    help = "Seed complete database with ALL fake data across all apps"

    def handle(self, *args, **kwargs):
        fake = Faker()
        
        self.stdout.write(self.style.WARNING('[*] Clearing ALL existing data...'))
        # Clear in dependency order
        Payment.objects.all().delete()
        InvoiceLine.objects.all().delete()
        Invoice.objects.all().delete()
        CoreInvoice.objects.all().delete()
        TransferLine.objects.all().delete()
        Transfer.objects.all().delete()
        StockTransaction.objects.all().delete()
        StockBatch.objects.all().delete()
        Product.objects.all().delete()
        CoreProduct.objects.all().delete()
        Warehouse.objects.all().delete()
        Customer.objects.all().delete()
        CoreCustomer.objects.all().delete()
        
        # ============ CORE APP DATA ============
        self.stdout.write(self.style.HTTP_INFO('\n[CORE] Creating Core App Data...'))
        
        # Core Products
        core_products = []
        for _ in range(50):
            product = CoreProduct.objects.create(
                name=f"{fake.word().capitalize()} {fake.word().capitalize()}",
                sku=fake.unique.bothify(text='CORE-#####'),
                price=Decimal(random.uniform(10, 500)).quantize(Decimal('0.01')),
                quantity=random.randint(1, 100)
            )
            core_products.append(product)
        self.stdout.write(f'  [OK] Created {len(core_products)} Core Products')

        # Core Customers
        core_customers = []
        for _ in range(20):
            customer = CoreCustomer.objects.create(
                name=fake.name(),
                email=fake.email(),
                phone=fake.phone_number()
            )
            core_customers.append(customer)
        self.stdout.write(f'  [OK] Created {len(core_customers)} Core Customers')

        # Core Invoices
        for _ in range(100):
            product = random.choice(core_products)
            customer = random.choice(core_customers)
            quantity = random.randint(1, 5)
            total_price = quantity * product.price
            
            CoreInvoice.objects.create(
                customer=customer,
                product=product,
                quantity=quantity,
                total_price=total_price
            )
        self.stdout.write(f'  [OK] Created 100 Core Invoices')

        # ============ INVENTORY APP DATA ============
        self.stdout.write(self.style.HTTP_INFO('\n[INVENTORY] Creating Inventory Data...'))
        
        # Warehouses
        warehouses = []
        warehouse_names = ['Main Warehouse', 'Secondary Storage', 'Distribution Center', 'North Depot']
        for name in warehouse_names:
            warehouse = Warehouse.objects.create(
                name=name,
                location=fake.address()
            )
            warehouses.append(warehouse)
        self.stdout.write(f'  [OK] Created {len(warehouses)} Warehouses')

        # Inventory Products
        products = []
        for _ in range(50):
            product = Product.objects.create(
                name=f"{fake.word().capitalize()} {fake.word().capitalize()}",
                sku=fake.unique.bothify(text='INV-???-####'),
                description=fake.sentence(nb_words=10),
                costing_method=random.choice(['FIFO', 'LIFO', 'AVG']),
                length=random.uniform(5, 50),
                width=random.uniform(5, 50),
                height=random.uniform(5, 50)
            )
            products.append(product)
        self.stdout.write(f'  [OK] Created {len(products)} Inventory Products')

        # Stock Batches
        batches = []
        for product in products:
            warehouse = random.choice(warehouses)
            num_batches = random.randint(1, 3)
            for _ in range(num_batches):
                batch = StockBatch.objects.create(
                    product=product,
                    warehouse=warehouse,
                    initial_qty=random.randint(20, 200),
                    current_qty=random.randint(5, 100),
                    unit_cost=Decimal(random.uniform(10, 500)).quantize(Decimal('0.01')),
                    received_date=fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.UTC),
                    reference=fake.bothify(text='BATCH-####')
                )
                batches.append(batch)
        self.stdout.write(f'  [OK] Created {len(batches)} Stock Batches')

        # Stock Transactions
        for _ in range(150):
            batch = random.choice(batches)
            StockTransaction.objects.create(
                batch=batch,
                transaction_type=random.choice(['PURCHASE', 'SALE', 'ADJUST', 'RETURN']),
                quantity=random.randint(-20, 20),
                reference_id=fake.bothify(text='TXN-#####')
            )
        self.stdout.write(f'  [OK] Created 150 Stock Transactions')

        # ============ SALES APP DATA ============
        self.stdout.write(self.style.HTTP_INFO('\n[SALES] Creating Sales Data...'))
        
        # Sales Customers
        customers = []
        for _ in range(30):
            customer = Customer.objects.create(
                name=fake.name(),
                email=fake.email(),
                phone=fake.phone_number()
            )
            customers.append(customer)
        self.stdout.write(f'  [OK] Created {len(customers)} Sales Customers')

        # Invoices with Lines
        invoices = []
        for _ in range(80):
            customer = random.choice(customers)
            warehouse = random.choice(warehouses)
            
            invoice = Invoice.objects.create(
                customer=customer,
                warehouse=warehouse,
                status=random.choice(['DRAFT', 'ISSUED', 'PAID'])
            )
            
            # Add 1-5 invoice lines
            total = Decimal(0)
            for _ in range(random.randint(1, 5)):
                product = random.choice(products)
                qty = random.randint(1, 10)
                price = Decimal(random.uniform(50, 500)).quantize(Decimal('0.01'))
                
                InvoiceLine.objects.create(
                    invoice=invoice,
                    product=product,
                    quantity=qty,
                    unit_price=price
                )
                total += qty * price
            
            invoice.total_amount = total
            invoice.save()
            invoices.append(invoice)
        
        self.stdout.write(f'  [OK] Created {len(invoices)} Invoices with Lines')

        # Payments
        for invoice in invoices:
            if invoice.status in ['ISSUED', 'PAID']:
                # Create 1-2 payments per invoice
                remaining = invoice.total_amount
                for _ in range(random.randint(1, 2)):
                    if remaining > 0:
                        amount = min(remaining, Decimal(random.uniform(100, float(remaining))).quantize(Decimal('0.01')))
                        Payment.objects.create(
                            invoice=invoice,
                            amount=amount,
                            method=random.choice(['CASH', 'CARD', 'BANK_TRANSFER'])
                        )
                        remaining -= amount
        self.stdout.write(f'  [OK] Created Payments')

        # ============ TRANSFERS APP DATA ============
        self.stdout.write(self.style.HTTP_INFO('\n[TRANSFERS] Creating Transfer Data...'))
        
        for _ in range(25):
            from_wh = random.choice(warehouses)
            to_wh = random.choice([w for w in warehouses if w != from_wh])
            
            transfer = Transfer.objects.create(
                source_warehouse=from_wh,
                dest_warehouse=to_wh,
                status=random.choice(['PENDING', 'APPROVED', 'SHIPPED', 'RECEIVED'])
            )
            
            # Add 1-4 transfer lines
            for _ in range(random.randint(1, 4)):
                product = random.choice(products)
                
                TransferLine.objects.create(
                    transfer=transfer,
                    product=product,
                    quantity=random.randint(5, 50)
                )
        
        self.stdout.write(f'  [OK] Created 25 Transfers with Lines')

        # ============ SUMMARY ============
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('*** SEEDING COMPLETE! ***'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f"""
[SUMMARY]
   - Core Products: {CoreProduct.objects.count()}
   - Core Customers: {CoreCustomer.objects.count()}
   - Core Invoices: {CoreInvoice.objects.count()}
   - Warehouses: {Warehouse.objects.count()}
   - Inventory Products: {Product.objects.count()}
   - Stock Batches: {StockBatch.objects.count()}
   - Stock Transactions: {StockTransaction.objects.count()}
   - Sales Customers: {Customer.objects.count()}
   - Sales Invoices: {Invoice.objects.count()}
   - Invoice Lines: {InvoiceLine.objects.count()}
   - Payments: {Payment.objects.count()}
   - Transfers: {Transfer.objects.count()}
   - Transfer Lines: {TransferLine.objects.count()}
        """)
