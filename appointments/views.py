from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from doctors.models import Doctor
from .models import Appointment

@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(patient=request.user)
    return render(request, "appointments/my_appointments.html", {
        "appointments": appointments
    })
def book_appointment(request):
    doctors = Doctor.objects.filter(available=True)

    if request.method == 'POST':
        doctor_id = request.POST['doctor']
        date = request.POST['date']

        Appointment.objects.create(
            patient=request.user,
            doctor_id=doctor_id,
            date=date
        )
        return redirect('my_appointments')

    return render(request, 'appointments/book.html', {'doctors': doctors})


@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(patient=request.user)
    return render(request, 'appointments/my_appointments.html', {'appointments': appointments})

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from doctors.models import Doctor
from .models import Appointment

@login_required
def doctor_appointments(request):
    doctor = Doctor.objects.get(user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor)

    return render(
        request,
        'appointments/doctor_appointments.html',
        {'appointments': appointments}
    )

@login_required
def update_appointment_status(request, pk, status):
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = status
    appointment.save()
    return redirect('doctor_appointments')

