from django.contrib import admin
from .models import Shift

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "clock_in_time",
        "clock_out_time",
        "is_approved",
        "created_at",
        "display_daily_pay"
    )
    list_filter = ("is_approved", "created_at")
    search_fields = ("user__username", "user__employee_code")

    def display_daily_pay(self, obj):
        return obj.calculate_daily_pay()
    display_daily_pay.short_description = "Daily Pay"