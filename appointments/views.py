from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import date as date_parser
from doctors.models import Doctor
from .models import Appointment

def _doctor_label(doctor):
    return doctor.user.get_full_name() or doctor.user.username


def _send_appointment_email(subject, message, recipient):
    if recipient:
        send_mail(subject, message, None, [recipient], fail_silently=True)


@login_required
def book_appointment(request):
    doctors = Doctor.objects.filter(available=True)

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        appointment_date = request.POST.get('date')
        doctor = get_object_or_404(Doctor, id=doctor_id, available=True)

        try:
            appointment_date = date_parser.fromisoformat(appointment_date)
        except (TypeError, ValueError):
            messages.error(request, "Please choose a valid appointment date.")
            return redirect('book_appointment')

        if appointment_date < timezone.localdate():
            messages.error(request, "Please choose today or a future date.")
            return redirect('book_appointment')

        appointment = Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            date=appointment_date
        )
        _send_appointment_email(
            "Appointment request received",
            f"Your appointment request with Dr. {_doctor_label(doctor)} on {appointment.date} is pending approval.",
            request.user.email,
        )
        messages.success(request, "Appointment requested successfully.")
        return redirect('my_appointments')

    return render(request, 'appointments/book.html', {'doctors': doctors})


@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(patient=request.user).select_related('doctor__user')
    return render(request, 'appointments/my_appointments.html', {'appointments': appointments})


@login_required
def doctor_appointments(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor).select_related('patient')

    return render(
        request,
        'appointments/doctor_appointments.html',
        {'appointments': appointments}
    )


@require_POST
@login_required
def update_appointment_status(request, pk, status):
    doctor = get_object_or_404(Doctor, user=request.user)
    appointment = get_object_or_404(Appointment, pk=pk, doctor=doctor)
    if status not in dict(Appointment.STATUS_CHOICES):
        messages.error(request, "Invalid appointment status.")
        return redirect('doctor_appointments')

    appointment.status = status
    if status != 'Rejected':
        appointment.reject_reason = ''
    appointment.save()
    _send_appointment_email(
        f"Appointment {status.lower()}",
        f"Your appointment with Dr. {_doctor_label(doctor)} on {appointment.date} was {status.lower()}.",
        appointment.patient.email,
    )
    messages.success(request, f"Appointment marked as {status.lower()}.")
    return redirect('doctor_appointments')


@require_POST
@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(
        Appointment,
        pk=pk,
        patient=request.user,
        status='Pending'
    )
    appointment.delete()
    messages.success(request, "Pending appointment cancelled.")
    return redirect('my_appointments')
