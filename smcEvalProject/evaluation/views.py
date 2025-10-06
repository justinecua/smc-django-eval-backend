from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response as DRFResponse
from rest_framework import status
from .serializer import EvaluationSerializer
from .models import Question, Evaluation
from .serializer import QuestionSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_evaluation(request):
    serializer = EvaluationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(evaluator=request.user)
        return DRFResponse({"message": "Evaluation submitted successfully"}, status=status.HTTP_201_CREATED)
    return DRFResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_questions(request):
    questions = Question.objects.all().order_by("id")
    serializer = QuestionSerializer(questions, many=True)
    return DRFResponse(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_evaluation_count(request):
    count = Evaluation.objects.filter(evaluator=request.user).count()
    return DRFResponse({"count": count}, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_evaluations(request):
    evaluations = Evaluation.objects.filter(evaluator=request.user).order_by("-date")
    serializer = EvaluationSerializer(evaluations, many=True)
    return DRFResponse(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_evaluation_detail(request, pk):
    try:
        evaluation = Evaluation.objects.get(pk=pk, evaluator=request.user)
    except Evaluation.DoesNotExist:
        return DRFResponse({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = EvaluationSerializer(evaluation)
    return DRFResponse(serializer.data, status=status.HTTP_200_OK)


# import io, os
# from django.http import HttpResponse
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework import permissions
# from PyPDF2 import PdfReader, PdfWriter
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from django.conf import settings
# from .models import Evaluation


# @api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
# def download_evaluation_pdf(request, pk):
#     try:
#         evaluation = Evaluation.objects.get(pk=pk, evaluator=request.user)
#     except Evaluation.DoesNotExist:
#         return HttpResponse({"error": "Not found"}, status=404)

#     template_path = os.path.join(settings.MEDIA_ROOT, "forms", "Evaluation.pdf")
#     if not os.path.exists(template_path):
#         return HttpResponse({"error": "Template not found"}, status=500)

#     # Read template
#     template_reader = PdfReader(open(template_path, "rb"))
#     template_page = template_reader.pages[0]

#     # Create overlay
#     packet = io.BytesIO()
#     can = canvas.Canvas(packet, pagesize=A4)
#     can.setFont("Helvetica", 10)

#     # --- Move overlay UP to bypass hidden top margin ---
#     can.translate(0, 150)  # ⬆️ Adjust this value (100–200) until perfectly aligned

#     # --- Calculate Y relative to top edge ---
#     page_width, page_height = A4  # (595, 842)
#     def from_top(distance):
#         """Convert 'distance from top' to reportlab y-position"""
#         return page_height - distance

#     # ✅ Example: place near the top-right of 'Name of Teacher' label
#     can.drawString(250, from_top(60), evaluation.teacher_name or "")

#     can.save()
#     packet.seek(0)

#     # Merge overlay with template
#     overlay_reader = PdfReader(packet)
#     overlay_page = overlay_reader.pages[0]
#     template_page.merge_page(overlay_page)

#     writer = PdfWriter()
#     writer.add_page(template_page)

#     response = HttpResponse(content_type="application/pdf")
#     response["Content-Disposition"] = f'attachment; filename=\"evaluation_{pk}.pdf\"'
#     writer.write(response)
#     return response
