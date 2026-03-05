from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance_home, name='attendance_home'),
    path('create-shift/', views.create_shift, name='create_shift'),
    path('clock-out/<int:shift_id>/', views.clock_out, name='clock_out'),
    path('start-break/<int:shift_id>/<str:break_type>/', views.start_break, name='start_break'),
    path('end-break/<int:shift_id>/<str:break_type>/', views.end_break, name='end_break'),
    path('logout/', views.logout_user, name='logout_user'),
]