from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import Specialty, Doctor, Appointment, CustomUser
from .forms import AppointmentForm, CustomUserCreationForm, GuestAppointmentForm
from django.utils import timezone
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def home(request):
    specialties = Specialty.objects.all()
    return render(request, 'bookings/home.html', {'specialties': specialties})


@login_required
def dashboard(request):
    if request.user.user_type == 'doctor':
        try:
            doctor = Doctor.objects.get(user=request.user)
            appointments = Appointment.objects.filter(
                doctor=doctor).order_by('-date', '-time')

            # Get counts for each status
            status_counts = appointments.values(
                'status').annotate(count=Count('status'))
            status_dict = {item['status']: item['count']
                           for item in status_counts}

            confirmed_count = status_dict.get('confirmed', 0)
            pending_count = status_dict.get('pending', 0)
            canceled_count = status_dict.get('canceled', 0)

            context = {
                'appointments': appointments[:10],
                'confirmed_count': confirmed_count,
                'pending_count': pending_count,
                'canceled_count': canceled_count,
            }
            template = 'bookings/doctor_dashboard.html'
        except Doctor.DoesNotExist:
            messages.error(
                request, "Doctor profile not found. Please contact admin.")
            return redirect('home')
    else:
        appointments = Appointment.objects.filter(
            patient=request.user).order_by('-date', '-time')
        doctors = Doctor.objects.all()[:4]

        context = {
            'appointments': appointments[:10],
            'doctors': doctors,
        }
        template = 'bookings/patient_dashboard.html'
    return render(request, template, context)


def doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    return render(request, 'bookings/doctor_detail.html', {'doctor': doctor})


def specialty_doctors(request, pk):
    specialty = get_object_or_404(Specialty, pk=pk)
    doctors = Doctor.objects.filter(specialty=specialty)
    return render(request, 'bookings/doctors_list.html', {
        'specialty': specialty,
        'doctors': doctors
    })


def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    if 'new_appointment' in request.GET:
        messages.success(
            request, 'Your appointment has been successfully booked!')

    return render(request, 'bookings/appointment_detail.html', {'appointment': appointment})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'bookings/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    else:
        form = AuthenticationForm()
    return render(request, 'bookings/login.html', {'form': form})


# ADDED LOGOUT VIEW FUNCTION
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')


@login_required
def book_appointment(request):
    doctors = Doctor.objects.all()
    selected_doctor_id = request.GET.get('doctor')

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        if not doctor_id:
            return render(request, 'bookings/book.html', {
                'form': AppointmentForm(request.POST),
                'doctors': doctors,
                'error': 'Please select a doctor'
            })

        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            return render(request, 'bookings/book.html', {
                'form': AppointmentForm(request.POST),
                'doctors': doctors,
                'error': 'Invalid doctor selected'
            })

        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.doctor = doctor
            appointment.save()
            return redirect(reverse('appointment_detail', kwargs={'pk': appointment.id}) + '?new_appointment=true')
        else:
            return render(request, 'bookings/book.html', {
                'form': form,
                'doctors': doctors
            })
    else:
        form = AppointmentForm()
        if selected_doctor_id:
            try:
                form.initial['doctor'] = Doctor.objects.get(
                    id=selected_doctor_id)
            except Doctor.DoesNotExist:
                pass

    return render(request, 'bookings/book.html', {
        'form': form,
        'doctors': doctors
    })


def guest_book_appointment(request):
    doctors = Doctor.objects.all()

    if request.method == 'POST':
        form = GuestAppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.status = 'pending'
            appointment.save()
            messages.success(
                request, 'Your appointment has been booked successfully!')
            return redirect(reverse('appointment_detail', kwargs={'pk': appointment.id}) + '?new_appointment=true')
    else:
        form = GuestAppointmentForm()

    return render(request, 'bookings/guest_book.html', {
        'form': form,
        'doctors': doctors
    })


@login_required
def doctor_dashboard(request):
    if not request.user.user_type == 'doctor':
        return redirect('dashboard')

    try:
        doctor = Doctor.objects.get(user=request.user)
        appointments_base = Appointment.objects.filter(
            doctor=doctor).order_by('-date', '-time')

        # Status filtering
        status = request.GET.get('status', 'all')
        if status != 'all':
            appointments = appointments_base.filter(status=status)
        else:
            appointments = appointments_base

        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            appointments = appointments.filter(
                Q(patient__first_name__icontains=search_query) |
                Q(patient__last_name__icontains=search_query) |
                Q(guest_name__icontains=search_query) |
                Q(reason__icontains=search_query)
            )

        # Status counts
        status_counts = appointments_base.values(
            'status').annotate(count=Count('status'))
        status_dict = {item['status']: item['count'] for item in status_counts}

        confirmed_count = status_dict.get('confirmed', 0)
        pending_count = status_dict.get('pending', 0)
        canceled_count = status_dict.get('canceled', 0)

        # Pagination
        paginator = Paginator(appointments, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Get recent appointments for activity log
        recent_appointments = appointments_base[:5]

        context = {
            'appointments': page_obj,
            'recent_appointments': recent_appointments,
            'confirmed_count': confirmed_count,
            'pending_count': pending_count,
            'canceled_count': canceled_count,
            'status_filter': status,
            'search_query': search_query,
            'doctor': doctor
        }
        return render(request, 'bookings/doctor_dashboard.html', context)
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor profile not found")
        return redirect('home')


def send_appointment_notification(appointment, action):
    """Send email notification for appointment status change"""
    if action == 'approved':
        subject = 'Your Appointment Has Been Confirmed'
        template = 'bookings/emails/appointment_confirmed.html'
    else:
        subject = 'Your Appointment Has Been Canceled'
        template = 'bookings/emails/appointment_canceled.html'

    # Determine recipient
    if appointment.patient:
        recipient = appointment.patient.email
        name = appointment.patient.get_full_name()
    else:
        recipient = appointment.guest_email
        name = appointment.guest_name

    if recipient:
        context = {
            'appointment': appointment,  # Added appointment object
            'name': name,
            'doctor': appointment.doctor.user.get_full_name(),
            'date': appointment.date,
            'time': appointment.time,
            'reason': appointment.reason,
            'action': action
        }

        html_message = render_to_string(template, context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            html_message=html_message,
            fail_silently=True
        )


@login_required
def appointment_action(request, pk, action):
    appointment = get_object_or_404(Appointment, pk=pk)

    if request.user != appointment.doctor.user:
        messages.error(request, "You don't have permission for this action")
        return redirect('doctor_dashboard')

    if action == 'approve':
        appointment.status = 'confirmed'
        appointment.save()
        messages.success(request, 'Appointment approved successfully')
        # Send notification email
        send_appointment_notification(appointment, 'approved')
    elif action == 'deny':
        appointment.status = 'canceled'
        appointment.save()
        messages.success(request, 'Appointment has been canceled')
        # Send notification email
        send_appointment_notification(appointment, 'canceled')
    else:
        messages.error(request, "Invalid action requested")
        return redirect('doctor_dashboard')

    return redirect('doctor_dashboard')
