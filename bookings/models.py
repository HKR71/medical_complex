from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.urls import reverse


class CustomUser(AbstractUser):
    PATIENT = 'patient'
    DOCTOR = 'doctor'
    USER_TYPES = [
        (PATIENT, 'Patient'),
        (DOCTOR, 'Doctor'),
    ]
    user_type = models.CharField(
        max_length=10, choices=USER_TYPES, default=PATIENT)
    phone = models.CharField(max_length=15, blank=True)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Specialty(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='fas fa-stethoscope')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('specialty_doctors', kwargs={'pk': self.pk})


class Doctor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='doctors/', blank=True, null=True)
    rating = models.FloatField(default=4.5)
    schedule_start = models.TimeField()
    schedule_end = models.TimeField()
    consultation_fee = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"

    def get_absolute_url(self):
        return reverse('doctor_detail', kwargs={'pk': self.pk})


class Appointment(models.Model):
    CONFIRMED = 'confirmed'
    PENDING = 'pending'
    CANCELED = 'canceled'
    STATUS_CHOICES = [
        (CONFIRMED, 'Confirmed'),
        (PENDING, 'Pending'),
        (CANCELED, 'Canceled'),
    ]

    patient = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='patient_appointments', null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField()
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    guest_name = models.CharField(max_length=100, blank=True, null=True)
    guest_phone = models.CharField(max_length=15, blank=True, null=True)
    guest_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"Appointment #{self.id}"

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
