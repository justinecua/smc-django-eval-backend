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