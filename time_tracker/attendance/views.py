from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from accounts.models import CustomUser
from .models import Shift
from .forms import ClockInForm, ClockOutForm
from breaks.forms import BreakForm
from breaks.models import Break

from django.shortcuts import render, redirect
from accounts.models import CustomUser  # your user model

from django.shortcuts import render, redirect
from accounts.models import CustomUser  # your user model

def login_by_code(request):
    error = None
    if request.method == "POST":
        code = request.POST.get("code")
        try:
            # 🔹 Use the correct field name
            user = CustomUser.objects.get(employee_code=code)
            request.session['user_id'] = user.id   # simple session login
            return redirect('dashboard')           # redirect to dashboard
        except CustomUser.DoesNotExist:
            error = "Invalid code"

    return render(request, "attendance/login_by_code.html", {"error": error})


# ✅ Dashboard
def dashboard(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_by_code")
    user = CustomUser.objects.get(id=user_id)
    shifts = user.shifts.all()

    # For active shift, check ongoing break
    active_shift = shifts.filter(clock_out_time__isnull=True).first()
    active_break = None
    if active_shift:
        active_break = active_shift.breaks.filter(end_time__isnull=True).first()

    return render(request, "attendance/dashboard.html", {
        "user": user,
        "shifts": shifts,
        "active_shift": active_shift,
        "active_break": active_break
    })


# ✅ Clock In
def clock_in(request):
    user_id = request.session.get("user_id")
    user = CustomUser.objects.get(id=user_id)

    if user.shifts.filter(clock_out_time__isnull=True).exists():
        messages.warning(request, "You already have an active shift")
        return redirect("dashboard")

    if request.method == "POST":
        form = ClockInForm(request.POST, request.FILES)
        if form.is_valid():
            shift = form.save(commit=False)
            shift.user = user
            shift.clock_in_time = timezone.now()
            shift.save()
            messages.success(request, "Clocked in successfully")
            return redirect("dashboard")
    else:
        form = ClockInForm()
    return render(request, "attendance/clock_in.html", {"form": form})


# ✅ Clock Out
def clock_out(request, shift_id):
    shift = get_object_or_404(Shift, id=shift_id)
    if shift.clock_out_time:
        messages.warning(request, "This shift is already clocked out")
        return redirect("dashboard")

    if request.method == "POST":
        form = ClockOutForm(request.POST, request.FILES, instance=shift)
        if form.is_valid():
            shift = form.save(commit=False)
            shift.clock_out_time = timezone.now()
            shift.save()
            messages.success(request, "Clocked out successfully")
            return redirect("dashboard")
    else:
        form = ClockOutForm(instance=shift)
    return render(request, "attendance/clock_out.html", {"form": form, "shift": shift})


# ✅ Start Break
def start_break(request, shift_id):
    shift = get_object_or_404(Shift, id=shift_id)
    if shift.breaks.filter(end_time__isnull=True).exists():
        messages.warning(request, "You already have an active break")
        return redirect("dashboard")

    if request.method == "POST":
        form = BreakForm(request.POST)
        if form.is_valid():
            brk = form.save(commit=False)
            brk.shift = shift
            brk.start_time = timezone.now()
            brk.save()
            messages.success(request, f"{brk.break_type} break started")
            return redirect("dashboard")
    else:
        form = BreakForm()
    return render(request, "attendance/start_break.html", {"form": form, "shift": shift})


# ✅ End Break
def end_break(request, break_id):
    brk = get_object_or_404(Break, id=break_id)
    brk.end_time = timezone.now()
    brk.save()
    messages.success(request, f"{brk.break_type} break ended")
    return redirect("dashboard")