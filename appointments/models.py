from django.db import models
from django.contrib.auth.models import User
from doctors.models import Doctor


class Appointment(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    REJECT_REASONS = [
        ('Not Available', 'Doctor not available'),
        ('Emergency', 'Doctor in emergency'),
        ('Time Conflict', 'Time conflict'),
        ('Invalid Details', 'Invalid patient details'),
        ('Clinic Closed', 'Clinic closed'),
        ('Other', 'Other'),
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    reject_reason = models.CharField(
        max_length=50,
        choices=REJECT_REASONS,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.patient.username} - {self.status}"
