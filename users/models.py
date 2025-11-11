from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
    ]

    full_name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    # manager uchun o'z do'koni (admin uchun null)
    store = models.ForeignKey('stock.Store', on_delete=models.SET_NULL, null=True, blank=True, related_name='managers')
    cache = models.PositiveIntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

    def get_role(self):
        return self.role
