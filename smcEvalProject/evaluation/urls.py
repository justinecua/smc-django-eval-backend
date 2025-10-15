from django.urls import path
from .views import (
    submit_evaluation, get_questions, get_user_evaluation_count,
    get_user_evaluations, get_evaluation_detail, download_evaluation_pdf
)

urlpatterns = [
    path("submit/", submit_evaluation, name="submit_evaluation"),
    path("questions/", get_questions, name="questions"),
    path("count/", get_user_evaluation_count, name="evaluation_count"),
    path("my-evaluations/", get_user_evaluations, name="my_evaluations"),
    path("my-evaluations/<int:pk>/", get_evaluation_detail, name="evaluation_detail"),
    path("my-evaluations/<int:pk>/download/", download_evaluation_pdf, name="download_evaluation_pdf"),
]
