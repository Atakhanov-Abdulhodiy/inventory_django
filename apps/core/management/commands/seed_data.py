from django.core.management.base import BaseCommand
from apps.core.models import Product, Customer, Invoice
from faker import Faker
import random
from decimal import Decimal

class Command(BaseCommand):
    help = "Seed the database with fake products, customers, and invoices"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Clearing existing data...'))
        Invoice.objects.all().delete()
        Product.objects.all().delete()
        Customer.objects.all().delete()

        fake = Faker()

        # 1. Create Products
        self.stdout.write('Creating 50 Products...')
        products = []
        for _ in range(50):
            product = Product.objects.create(
                name=f"{fake.word().capitalize()} {fake.word().capitalize()}",
                sku=fake.unique.bothify(text='??-#####'),
                price=Decimal(random.uniform(10, 500)).quantize(Decimal('0.01')),
                quantity=random.randint(1, 100)
            )
            products.append(product)

        # 2. Create Customers
        self.stdout.write('Creating 20 Customers...')
        customers = []
        for _ in range(20):
            customer = Customer.objects.create(
                name=fake.name(),
                email=fake.email(),
                phone=fake.phone_number()
            )
            customers.append(customer)

        # 3. Create Invoices
        self.stdout.write('Creating 100 Invoices...')
        for _ in range(100):
            product = random.choice(products)
            customer = random.choice(customers)
            quantity = random.randint(1, 5)
            total_price = quantity * product.price
            
            Invoice.objects.create(
                customer=customer,
                product=product,
                quantity=quantity,
                total_price=total_price
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(products)} products, {len(customers)} customers, and 100 invoices.'))
