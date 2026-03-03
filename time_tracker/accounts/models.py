from django.contrib.auth.models import AbstractUser
from django.db import models
import random

class CustomUser(AbstractUser):
    employee_code = models.CharField(max_length=4, unique=True)

    def save(self, *args, **kwargs):
        if not self.employee_code:
            self.employee_code = str(random.randint(1000, 9999))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.employee_code})"
