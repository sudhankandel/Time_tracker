from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_by_code, name="login_by_code"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("clock_in/", views.clock_in, name="clock_in"),
    path("clock_out/<int:shift_id>/", views.clock_out, name="clock_out"),
    path("start_break/<int:shift_id>/", views.start_break, name="start_break"),
    path("end_break/<int:break_id>/", views.end_break, name="end_break"),
]