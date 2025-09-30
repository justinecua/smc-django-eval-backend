from django.db import models
from django.conf import settings


class Teacher(models.Model):
    name = models.CharField(max_length=255, unique=True)
    college = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    room_number = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Evaluation(models.Model):
    teacher_name = models.CharField(max_length=255, null=True, blank=True)
    college = models.CharField(max_length=255, null=True, blank=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    room_number = models.CharField(max_length=50, null=True, blank=True)

    evaluator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    date = models.DateField()
    time_of_observation = models.TimeField()
    other_comments = models.TextField(blank=True)

    average_rating = models.FloatField(null=True, blank=True)

    date_of_conference = models.DateField(null=True, blank=True)
    time_of_conference = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.teacher_name} ({self.date})"


class Question(models.Model):
    CATEGORY_CHOICES = [
        ("content", "Content"),
        ("teaching", "Teaching Procedures"),
        ("interaction", "Teacher-Student Interaction"),
    ]

    text = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.text[:50]


RATING_CHOICES = [
    (5, "Excellent"),
    (4, "Very Good"),
    (3, "Good"),
    (2, "Fair"),
    (1, "Poor"),
    (0, "Not Applicable"),
]


class Response(models.Model):
    evaluation = models.ForeignKey(
        Evaluation, on_delete=models.CASCADE, related_name="responses"
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        unique_together = ("evaluation", "question")

    def __str__(self):
        return f"{self.evaluation} - {self.question}"
