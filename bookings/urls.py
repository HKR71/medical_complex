from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('book/', views.book_appointment, name='book'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('doctor/<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('appointment/<int:pk>/', views.appointment_detail,
         name='appointment_detail'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('guest-book/', views.guest_book_appointment, name='guest_book'),
    path('appointment/<int:pk>/<str:action>/',
         views.appointment_action, name='appointment_action'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),

    # NEW: Doctors by specialty
    path('specialty/<int:pk>/doctors/',
         views.specialty_doctors, name='specialty_doctors'),
]
