from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book_appointment, name='book_appointment'),
    path('my/', views.my_appointments, name='my_appointments'),
    path('doctor/', views.doctor_appointments, name='doctor_appointments'),
    path('doctor/<int:pk>/<str:status>/', views.update_appointment_status, name='update_status'),
    path('<int:pk>/cancel/', views.cancel_appointment, name='cancel_appointment'),
]
