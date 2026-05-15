from django.contrib import admin
from .models import Doctor

class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'available')
    list_filter = ('available', 'specialization')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'specialization')

admin.site.register(Doctor, DoctorAdmin)

admin.site.site_header = "VRAJ Care Admin"
admin.site.site_title = "VRAJ Care Portal"
admin.site.index_title = "Welcome to VRAJ Care Admin Panel"
