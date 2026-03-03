from django.db import models
from django.utils import timezone

class Break(models.Model):

    BREAK_TYPE = (
        ("PAID", "Paid"),
        ("UNPAID", "Unpaid"),
    )

    shift = models.ForeignKey(
        "attendance.Shift",  # string reference to avoid circular import
        on_delete=models.CASCADE,
        related_name="breaks"
    )

    break_type = models.CharField(max_length=10, choices=BREAK_TYPE)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)

    def duration(self):
        if self.end_time:
            return self.end_time - self.start_time
        return None

    def __str__(self):
        return f"{self.shift.user.username} - {self.break_type}"