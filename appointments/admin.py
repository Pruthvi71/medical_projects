from django.contrib import admin
from .models import Appointment

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'status', 'reject_reason')
    list_filter = ('status', 'doctor', 'date')
    search_fields = ('patient__username', 'patient__email', 'doctor__user__username')
    date_hierarchy = 'date'

admin.site.register(Appointment, AppointmentAdmin)
