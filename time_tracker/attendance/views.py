from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import CustomUser
from attendance.models import Shift
from breaks.models import Break


# ==========================================
# HOME (Login + Dashboard in same page)
# ==========================================
def attendance_home(request):
    users = CustomUser.objects.filter(is_staff=False)
    selected_user = None
    shifts = None
    is_logged_in = False

    user_id = request.session.get("user_id")

    # If already logged in
    if user_id:
        try:
            selected_user = CustomUser.objects.get(id=user_id)
            shifts = Shift.objects.filter(user=selected_user).order_by("-clock_in_time")
            is_logged_in = True
        except CustomUser.DoesNotExist:
            del request.session["user_id"]

    # Login via employee code
    if request.method == "POST" and not is_logged_in:
        user_id_form = request.POST.get("user_id")
        code = request.POST.get("employee_code")

        if user_id_form and code:
            try:
                selected_user = CustomUser.objects.get(
                    id=user_id_form,
                    employee_code=code
                )
                request.session["user_id"] = selected_user.id
                shifts = Shift.objects.filter(user=selected_user).order_by("-clock_in_time")
                is_logged_in = True
            except CustomUser.DoesNotExist:
                messages.error(request, "Invalid 4-digit code")

    return render(request, "attendance/home.html", {
        "users": users,
        "selected_user": selected_user,
        "shifts": shifts,
        "is_logged_in": is_logged_in
    })


# ==========================================
# CREATE SHIFT
# ==========================================
@require_POST
def create_shift(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("attendance_home")

    user = CustomUser.objects.get(id=user_id)

    # Prevent multiple running shifts
    running_shift = Shift.objects.filter(
        user=user,
        clock_out_time__isnull=True
    ).first()

    if not running_shift:
        Shift.objects.create(
            user=user,
            clock_in_time=timezone.now()
        )

    return redirect("attendance_home")


from decimal import Decimal

# ==========================================
# CLOCK OUT (END SHIFT)
# ==========================================
def clock_out(request, shift_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("attendance_home")

    user = CustomUser.objects.get(id=user_id)
    shift = get_object_or_404(Shift, id=shift_id, user=user)

    if not shift.clock_out_time:
        shift.clock_out_time = timezone.now()

        # Calculate total seconds
        total_seconds = (shift.clock_out_time - shift.clock_in_time).total_seconds()

        # Break calculations
        unpaid_break = sum([b.duration() for b in shift.breaks.filter(break_type="unpaid")])

        # Total hours as Decimal
        shift.total_hours = Decimal(total_seconds - unpaid_break) / Decimal(3600)

        # Total pay as Decimal
        shift.total_pay = shift.total_hours * user.hourly_rate

        shift.save()

    return redirect("attendance_home")


# ==========================================
# START BREAK
# ==========================================
def start_break(request, shift_id, break_type):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("attendance_home")

    shift = get_object_or_404(Shift, id=shift_id, user_id=user_id)

    # Prevent multiple active same-type breaks
    active_break = shift.breaks.filter(
        break_type=break_type,
        end_time__isnull=True
    ).exists()

    if not active_break:
        Break.objects.create(
            shift=shift,
            break_type=break_type,
            start_time=timezone.now()
        )

    return redirect("attendance_home")


# ==========================================
# END BREAK
# ==========================================
def end_break(request, shift_id, break_type):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("attendance_home")

    shift = get_object_or_404(Shift, id=shift_id, user_id=user_id)

    active_break = shift.breaks.filter(
        break_type=break_type,
        end_time__isnull=True
    ).last()

    if active_break:
        active_break.end_time = timezone.now()
        active_break.save()

    return redirect("attendance_home")


# ==========================================
# LOGOUT (Optional but recommended)
# ==========================================
from django.views.decorators.http import require_POST

@require_POST
def logout_user(request):
    request.session.flush()
    return redirect("attendance_home")