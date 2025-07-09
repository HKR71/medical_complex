from .models import Appointment
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Doctor
from django.utils import timezone


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'user_type', 'phone')
        widgets = {
            'user_type': forms.RadioSelect(choices=CustomUser.USER_TYPES),
            'phone': forms.TextInput(attrs={'placeholder': '+1234567890'})
        }


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'time', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'min': timezone.now().date().isoformat(),
                'class': 'form-control'
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'reason': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Describe your symptoms or reason for visit'
            }),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date < timezone.now().date():
            raise forms.ValidationError(
                "Appointment date cannot be in the past")
        return date


class GuestAppointmentForm(forms.ModelForm):
    guest_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Full Name'
    }))
    guest_phone = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone Number'
    }))
    guest_email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email Address'
    }))

    class Meta:
        model = Appointment
        fields = ['guest_name', 'guest_phone', 'guest_email',
                  'doctor', 'date', 'time', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'min': timezone.now().date().isoformat(),
                'class': 'form-control'
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'reason': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Describe your symptoms or reason for visit'
            }),
            'doctor': forms.Select(attrs={'class': 'form-select form-select-lg'})
        }
