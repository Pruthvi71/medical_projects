from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Doctor
from appointments.models import Appointment

def doctor_dashboard(request):
    doctor = Doctor.objects.get(user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor)

    return render(request, "doctors/dashboard.html", {
        "appointments": appointments
    })
    
def doctor_login(request):
    if request.user.is_authenticated:
        return redirect('doctor_dashboard')

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
    doctor = Doctor.objects.get(user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor)

    return render(request, "doctors/dashboard.html", {
        "doctor": doctor,
        "appointments": appointments
    })


@login_required
def approve_appointment(request, id):
    doctor = Doctor.objects.get(user=request.user)
    appointment = Appointment.objects.get(id=id, doctor=doctor)

    appointment.status = "Approved"
    appointment.reject_reason = ""
    appointment.save()

    return redirect('doctor_dashboard')


@login_required
def reject_appointment(request, id):
    doctor = Doctor.objects.get(user=request.user)
    appointment = Appointment.objects.get(id=id, doctor=doctor)

    if request.method == "POST":
        reason = request.POST.get('reason')
        appointment.status = "Rejected"
        appointment.reject_reason = reason
        appointment.save()
        return redirect('doctor_dashboard')

    return render(request, "doctors/reject_reason.html", {
        "appointment": appointment,
        "reasons": Appointment.REJECT_REASONS
    })


def doctor_logout(request):
    logout(request)
    request.session.flush() 
    return redirect('/')
