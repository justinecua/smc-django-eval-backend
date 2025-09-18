from django.contrib.auth.models import User
from django.db import models

class PersonnelInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=200, blank=True, null=True)
    position = models.CharField(max_length=200, blank=True, null=True)
    employID = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.user.username
