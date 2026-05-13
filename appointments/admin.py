from django.contrib import admin
from .models import Appointment

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'status')
    list_filter = ('status', 'doctor')
    search_fields = ('patient__username',)

admin.site.register(Appointment, AppointmentAdmin)