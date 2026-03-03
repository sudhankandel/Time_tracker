from django.utils import timezone
from .models import Shift

# ✅ Clock In
def clock_in_user(user, image):

    # Check if active shift already exists
    active_shift = Shift.objects.filter(
        user=user,
        clock_out_time__isnull=True
    ).first()

    if active_shift:
        raise Exception("User already clocked in.")

    shift = Shift.objects.create(
        user=user,
        clock_in_time=timezone.now(),
        clock_in_image=image
    )

    return shift


# ✅ Clock Out
def clock_out_user(user, image):

    shift = Shift.objects.filter(
        user=user,
        clock_out_time__isnull=True
    ).first()

    if not shift:
        raise Exception("No active shift found.")

    shift.clock_out_time = timezone.now()
    shift.clock_out_image = image
    shift.save()

    return shift