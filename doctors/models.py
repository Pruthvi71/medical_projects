from django.db import models
from django.contrib.auth.models import User

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    available = models.BooleanField(default=True)

    @property
    def display_name(self):
        return self.user.get_full_name() or self.user.username

    def __str__(self):
        return self.display_name
