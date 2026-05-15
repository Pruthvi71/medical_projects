from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.views.decorators.http import require_POST

from .models import Doctor
from appointments.models import Appointment

def doctor_login(request):
    if request.user.is_authenticated:
        if Doctor.objects.filter(user=request.user).exists():
            return redirect('doctor_dashboard')
        messages.error(request, "You are logged in as a patient. Please logout before using the doctor portal.")
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if Doctor.objects.filter(user=user).exists():
                login(request, user)
                return redirect('doctor_dashboard')
            else:
                messages.error(request, "You are not registered as a doctor")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "doctors/login.html")


@login_required
def doctor_dashboard(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor).select_related('patient')

    return render(request, "doctors/dashboard.html", {
        "doctor": doctor,
        "appointments": appointments,
        "pending_count": appointments.filter(status='Pending').count(),
        "approved_count": appointments.filter(status='Approved').count(),
        "rejected_count": appointments.filter(status='Rejected').count(),
    })


@require_POST
@login_required
def approve_appointment(request, id):
    doctor = get_object_or_404(Doctor, user=request.user)
    appointment = get_object_or_404(Appointment, id=id, doctor=doctor)

    appointment.status = "Approved"
    appointment.reject_reason = ""
    appointment.save()
    if appointment.patient.email:
        send_mail(
            "Appointment approved",
            f"Your appointment with Dr. {doctor.user.get_full_name() or doctor.user.username} on {appointment.date} was approved.",
            None,
            [appointment.patient.email],
            fail_silently=True,
        )
    messages.success(request, "Appointment approved.")

    return redirect('doctor_dashboard')


@require_POST
@login_required
def reject_appointment(request, id):
    doctor = get_object_or_404(Doctor, user=request.user)
    appointment = get_object_or_404(Appointment, id=id, doctor=doctor)

    reason = request.POST.get('reason')
    if reason not in dict(Appointment.REJECT_REASONS):
        messages.error(request, "Please choose a valid rejection reason.")
        return redirect('doctor_dashboard')

    appointment.status = "Rejected"
    appointment.reject_reason = reason
    appointment.save()
    if appointment.patient.email:
        send_mail(
            "Appointment rejected",
            f"Your appointment with Dr. {doctor.user.get_full_name() or doctor.user.username} on {appointment.date} was rejected. Reason: {appointment.get_reject_reason_display()}",
            None,
            [appointment.patient.email],
            fail_silently=True,
        )
    messages.success(request, "Appointment rejected.")
    return redirect('doctor_dashboard')


def doctor_logout(request):
    logout(request)
    request.session.flush() 
    return redirect('/')
