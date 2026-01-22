from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Consultation
from .serializer import ConsultationSerializer
import io, os
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4   
from django.conf import settings
from .models import Consultation
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def submit_consultation(request):
    serializer = ConsultationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user) 
        return Response({"message": "Consultation submitted successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_user_consultations(request):
    consultations = Consultation.objects.filter(user=request.user).order_by("-created_at")
    serializer = ConsultationSerializer(consultations, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_consultation_detail(request, pk):
    try:
        consultation = Consultation.objects.get(pk=pk, user=request.user)
    except Consultation.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = ConsultationSerializer(consultation)
    return Response(serializer.data)

@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def delete_consultation(request, pk):
    try:
        consultation = Consultation.objects.get(pk=pk, user=request.user)
        consultation.delete()
        return Response({"message": "Consultation deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Consultation.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

def draw_paragraph(can, text, x, y, max_width, max_height):
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontName = "Helvetica"
    style.fontSize = 10

    p = Paragraph(text or "N/A", style)
    w, h = p.wrap(max_width, max_height)   
    p.drawOn(can, x, y - h)             

def draw_wrapped_text(can, text, x, y, max_width, line_height=12):
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
def download_consultation_pdf(request, pk):
    try:
        consultation = Consultation.objects.get(pk=pk, user=request.user)
    except Consultation.DoesNotExist:
        return HttpResponse("Not found", status=404)

    template_path = os.path.join(settings.MEDIA_ROOT, "forms", "Consultation.pdf")
    if not os.path.exists(template_path):
        return HttpResponse("Template PDF not found", status=500)

    template_reader = PdfReader(open(template_path, "rb"))
    template_page = template_reader.pages[0]

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    can.setFont("Helvetica", 10)

    can.drawString(107, 795, consultation.college or "")
    can.drawString(107, 773, str(consultation.date) if consultation.date else "")
    can.drawString(107, 750, str(consultation.time) if consultation.time else "")
    can.drawString(107, 730, consultation.venue or "")

    can.drawString(145, 685, consultation.student_name or "")
    can.drawString(482, 685, consultation.course_year or "")
    can.drawString(84, 665, consultation.subject or "")
    can.drawString(385, 665, consultation.course_description or "")
    can.drawString(125, 642, consultation.class_schedule or "")
    can.drawString(425, 642, consultation.room_number or "")
    can.drawString(107, 620, consultation.school_year or "")
    can.drawString(322, 620, consultation.semester or "")
    can.drawString(460, 620, consultation.term or "")
    can.drawString(120, 600, consultation.subject_grade or "")

    draw_wrapped_text(can, consultation.difficulties_identified or "N/A", 52, 550, 236)
    draw_wrapped_text(can, consultation.remarks or "N/A", 325, 550, 236)
    draw_wrapped_text(can, consultation.learning_assistance or "N/A", 52, 425, 505)
    draw_wrapped_text(can, consultation.resolution or "N/A", 52, 275, 505)

    can.save()
    packet.seek(0)

    overlay_reader = PdfReader(packet)
    overlay_page = overlay_reader.pages[0]
    template_page.merge_page(overlay_page)

    writer = PdfWriter()
    writer.add_page(template_page)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="consultation_{pk}.pdf"'
    writer.write(response)
    return response

