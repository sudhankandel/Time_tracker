from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_home, name='attendance_home'),  # dashboard
    path('shift/<int:shift_id>/clock_in/', views.clock_in, name='clock_in'),
    path('shift/<int:shift_id>/clock_out/', views.clock_out, name='clock_out'),
    path('shift/<int:shift_id>/break/<str:break_type>/start/', views.start_break, name='start_break'),
    path('shift/<int:shift_id>/break/<str:break_type>/end/', views.end_break, name='end_break'),
]