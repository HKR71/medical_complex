from django.contrib import admin
from .models import CustomUser, Specialty, Doctor, Appointment


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'user_type')
    list_filter = ('user_type',)
    search_fields = ('username', 'email', 'first_name', 'last_name')


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty', 'consultation_fee', 'rating')
    search_fields = ('user__first_name', 'user__last_name')
    list_filter = ('specialty',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'time', 'status')
    list_filter = ('status', 'date')
    search_fields = ('patient__username', 'doctor__user__last_name')
