from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import Decimal
import random

class CustomUser(AbstractUser):
    """
    Custom User Model for Time Tracking System
    """

    employee_code = models.CharField(
        max_length=4,
        unique=True,
        blank=True
    )

    hourly_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00")
    )

    profile_image = models.ImageField(
        upload_to="profiles/",
        null=True,
        blank=True
    )

    ROLE_CHOICES = (
        ("EMPLOYEE", "Employee"),
        ("ADMIN", "Admin"),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="EMPLOYEE"
    )

    def save(self, *args, **kwargs):
        if not self.employee_code:
            self.employee_code = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        while True:
            code = str(random.randint(1000, 9999))
            if not CustomUser.objects.filter(employee_code=code).exists():
                return code

    def __str__(self):
        return f"{self.username} ({self.employee_code})"

    def get_hourly_rate(self):
        return self.hourly_rate