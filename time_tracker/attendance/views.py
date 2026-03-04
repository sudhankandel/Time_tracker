from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import CustomUser
from attendance.models import Shift
from breaks.models import Break
from django.utils import timezone

from django.shortcuts import render
from django.contrib import messages
from accounts.models import CustomUser
from attendance.models import Shift

def attendance_home(request):
    users = CustomUser.objects.filter(is_staff=False)
    selected_user = None
    shifts = None
    is_logged_in = False

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        code = request.POST.get("employee_code")

        if user_id and code:
            try:
                selected_user = CustomUser.objects.get(
                    id=user_id,
                    employee_code=code
                )
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

def clock_in(request, shift_id):
    shift = get_object_or_404(Shift, id=shift_id)
    shift.clock_in_time = timezone.now()
    shift.save()
    return redirect('attendance_home', user_id=shift.user.id)

def clock_out(request, shift_id):
    shift = get_object_or_404(Shift, id=shift_id)
    shift.clock_out_time = timezone.now()
    shift.save()
    return redirect('attendance_home', user_id=shift.user.id)

def start_break(request, shift_id, break_type):
    shift = get_object_or_404(Shift, id=shift_id)
    Break.objects.create(shift=shift, break_type=break_type.upper())
    return redirect('attendance_home', user_id=shift.user.id)

def end_break(request, shift_id, break_type):
    shift = get_object_or_404(Shift, id=shift_id)
    active_break = shift.breaks.filter(break_type=break_type.upper(), end_time__isnull=True).last()
    if active_break:
        active_break.end_time = timezone.now()
        active_break.save()
    return redirect('attendance_home', user_id=shift.user.id)

# --- Login by employee_code ---
def login_by_code(request):
    error = None
    if request.method == "POST":
        code = request.POST.get("code")
        try:
            user = CustomUser.objects.get(employee_code=code)
            request.session['user_id'] = user.id
            return redirect('dashboard')
        except CustomUser.DoesNotExist:
            error = "Invalid code"
    return render(request, "attendance/login_by_code.html", {"error": error})

# --- Dashboard ---
def dashboard(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login_by_code')

    user = CustomUser.objects.get(id=user_id)
    shifts = Shift.objects.filter(user=user).order_by('-clock_in_time')  # previous shifts

    return render(request, "attendance/dashboard.html", {"user": user, "shifts": shifts})

# --- Clock in ---
def clock_in(request, shift_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login_by_code')

    user = CustomUser.objects.get(id=user_id)
    shift = get_object_or_404(Shift, id=shift_id, user=user)

    if not shift.clock_in_time:
        shift.clock_in_time = timezone.now()
        shift.save()
    return redirect('dashboard')

# --- Clock out ---
def clock_out(request, shift_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login_by_code')

    user = CustomUser.objects.get(id=user_id)
    shift = get_object_or_404(Shift, id=shift_id, user=user)

    if not shift.clock_out_time:
        shift.clock_out_time = timezone.now()
        # Calculate total hours minus breaks
        total_seconds = (shift.clock_out_time - shift.clock_in_time).total_seconds()
        paid_break = sum([b.duration() for b in shift.breaks.filter(break_type='paid')])
        unpaid_break = sum([b.duration() for b in shift.breaks.filter(break_type='unpaid')])
        shift.total_hours = (total_seconds - unpaid_break) / 3600  # total hours excluding unpaid
        shift.total_pay = shift.total_hours * user.hourly_rate
        shift.save()
    return redirect('dashboard')

# --- Start Break ---
def start_break(request, shift_id, break_type):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login_by_code')

    shift = get_object_or_404(Shift, id=shift_id, user_id=user_id)
    b = Break.objects.create(shift=shift, break_type=break_type, start_time=timezone.now())
    b.save()
    return redirect('dashboard')

# --- End Break ---
def end_break(request, shift_id, break_type):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login_by_code')

    shift = get_object_or_404(Shift, id=shift_id, user_id=user_id)
    b = shift.breaks.filter(break_type=break_type, end_time__isnull=True).last()
    if b:
        b.end_time = timezone.now()
        b.save()
    return redirect('dashboard')