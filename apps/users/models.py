from django.contrib.auth.models import AbstractUser
from django.db import models

class UserProfile(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('WAREHOUSE_MGR', 'Warehouse Manager'),
        ('SALES_STAFF', 'Sales Staff'),
        ('ACCOUNTANT', 'Accountant'),
        ('CEO', 'CEO'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='SALES_STAFF')
    kpi_score = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"
