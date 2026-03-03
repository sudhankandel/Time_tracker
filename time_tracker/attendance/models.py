from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

class Shift(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shifts"
    )
    clock_in_time = models.DateTimeField(null=True, blank=True)
    clock_out_time = models.DateTimeField(null=True, blank=True)
    clock_in_image = models.ImageField(upload_to="clock_in/")
    clock_out_image = models.ImageField(upload_to="clock_out/", null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-clock_in_time']

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"

    def is_active(self):
        return self.clock_in_time and not self.clock_out_time

    def total_shift_duration(self):
        if self.clock_in_time and self.clock_out_time:
            return self.clock_out_time - self.clock_in_time
        return timedelta(0)

    def total_unpaid_break(self):
        unpaid_breaks = self.breaks.filter(
            break_type="UNPAID",
            end_time__isnull=False
        )
        total = timedelta(0)
        for b in unpaid_breaks:
            total += b.duration()
        return total

    def actual_working_duration(self):
        return self.total_shift_duration() - self.total_unpaid_break()

    def calculate_daily_pay(self):
        actual_duration = self.actual_working_duration()
        hours = actual_duration.total_seconds() / 3600
        return Decimal(hours) * self.user.hourly_rate