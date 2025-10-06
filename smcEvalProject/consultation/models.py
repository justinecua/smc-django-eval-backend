from django.db import models
from django.conf import settings 


class Consultation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="consultations"
    )

    college = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    venue = models.CharField(max_length=255)

    student_name = models.CharField(max_length=255)
    course_year = models.CharField(max_length=100)
    subject = models.CharField(max_length=255)
    course_description = models.CharField(max_length=255)
    class_schedule = models.CharField(max_length=100)
    room_number = models.CharField(max_length=50, blank=True, null=True)
    school_year = models.CharField(max_length=20)
    semester = models.CharField(max_length=20)
    term = models.CharField(max_length=20)
    subject_grade = models.CharField(max_length=20, blank=True, null=True)

    difficulties_identified = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    learning_assistance = models.TextField(blank=True, null=True)
    resolution = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Consultation - {self.student_name} by {self.user.username}"
