from django.urls import path
from .views import submit_consultation, get_user_consultations, get_consultation_detail, delete_consultation, download_consultation_pdf

urlpatterns = [
    path("submit/", submit_consultation, name="submit_consultation"),
    path("my-consultations/", get_user_consultations, name="my_consultations"),
    path("my-consultations/<int:pk>/", get_consultation_detail, name="consultation_detail"),
    path("my-consultations/<int:pk>/delete/", delete_consultation, name="consultation_delete"),
    path("my-consultations/<int:pk>/pdf/", download_consultation_pdf, name="consultation_pdf"),
]
