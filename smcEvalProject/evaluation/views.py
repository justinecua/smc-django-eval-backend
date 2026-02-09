
import io, os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response as DRFResponse
from rest_framework import status
from .serializer import EvaluationSerializer
from .models import Question, Evaluation
from .serializer import QuestionSerializer
from django.http import HttpResponse
from rest_framework import permissions
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.conf import settings
from .models import Evaluation, Response
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.http import JsonResponse


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

def draw_paragraph(can, text, x, y, max_width, max_height):
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontName = "Helvetica"
    style.fontSize = 10

    p = Paragraph(text or "N/A", style)
    w, h = p.wrap(max_width, max_height)   
    p.drawOn(can, x, y - h)             


def draw_wrapped_text(can, text, x, y, max_width, line_height=12):
    """Draws text that wraps automatically when it reaches the max width."""
    if not text:
        return
    line = ""
    for char in text:
        test_line = line + char
        if stringWidth(test_line, "Helvetica", 10) <= max_width:
            line = test_line
        else:
            can.drawString(x, y, line)
            y -= line_height
            line = char
    if line:
        can.drawString(x, y, line)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def download_evaluation_pdf(request, pk):
    try:
        evaluation = Evaluation.objects.get(pk=pk, evaluator=request.user)
    except Evaluation.DoesNotExist:
        return HttpResponse({"error": "Not found"}, status=404)

    template_path = os.path.join(settings.MEDIA_ROOT, "forms", "Evaluation.pdf")
    if not os.path.exists(template_path):
        return HttpResponse({"error": "Template not found"}, status=500)

    template_reader = PdfReader(open(template_path, "rb"))
    template_page = template_reader.pages[0]

    media_box = template_page.mediabox
    page_width = float(media_box.width)
    page_height = float(media_box.height)

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(page_width, page_height))
    can.setFont("Helvetica", 10)

    can.drawString(131, page_height - 148, evaluation.teacher_name or "")
    can.drawString(340, page_height - 148, evaluation.date.strftime("%m/%d/%Y") if evaluation.date else "")
    can.drawString(520, page_height - 148,
                   evaluation.time_of_observation.strftime("%I:%M %p") if evaluation.time_of_observation else "")
    can.drawString(85, page_height - 162, evaluation.college or "")
    can.drawString(400, page_height - 162, evaluation.room_number or "")
    can.drawString(85, page_height - 175, evaluation.subject or "")

    responses = Response.objects.filter(evaluation=evaluation).order_by("id")

    #remarks
    rating_positions = [
        #1    2    3    4    5    6    7    8    9    10
        260, 275, 289, 313, 337, 363, 377, 390, 426, 441,
        #11   12   13   14   15   16   17   18   19   20 
        453, 490, 517, 553, 566, 590, 642, 667, 681, 694,
        #21   #22
        707,730
    ]

    # Ratings loop
    for i, r in enumerate(responses):
        if i < len(rating_positions):
            y = page_height - rating_positions[i]
            can.drawString(545, y, f"{r.rating}")

    # Average Rating
    if evaluation.average_rating is not None:
        avg_rating_text = f"{float(evaluation.average_rating):.2f}"
        last_rating_y = page_height - rating_positions[-1]
        can.drawString(510, last_rating_y - 24, avg_rating_text)

    # Other Comments
    comment_x = 150          
    comment_y = page_height - 780  
    max_comment_width = 419 
    draw_wrapped_text(can, evaluation.other_comments, comment_x, comment_y, max_comment_width, line_height=13)

    #evaluator
    full_name = ""
    if evaluation.evaluator:
        full_name = f"{evaluation.evaluator.first_name or ''} {evaluation.evaluator.last_name or ''}".strip()
    x = 405

    if len(full_name) <= 15:
        x += 60  # shift right
    elif len(full_name) > 20:
        x += 10  # shift left
    can.drawString(x, page_height - 844, full_name or "")

    #date of conference
    can.drawString(138, page_height - 895, evaluation.date.strftime("%m/%d/%Y") if evaluation.date_of_conference else "")

    #time of conference
    can.drawString(330, page_height - 895,                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
                   evaluation.time_of_conference.strftime("%I:%M %p") if evaluation.time_of_conference else "")
    
    can.save()
    packet.seek(0)
                                                                                                                                                                                        
    overlay_reader = PdfReader(packet)
    overlay_page = overlay_reader.pages[0]
    template_page.merge_page(overlay_page)

    writer = PdfWriter()
    writer.add_page(template_page)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="evaluation_{pk}.pdf"'
    writer.write(response)
    return response
