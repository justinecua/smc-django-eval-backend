from rest_framework import serializers
from .models import Evaluation, Response, Question

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "text", "category"]

class ResponseReadSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = Response
        fields = ["id", "question", "rating", "remarks"]

class ResponseWriteSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())

    class Meta:
        model = Response
        fields = ["id", "question", "rating", "remarks"]

class EvaluationSerializer(serializers.ModelSerializer):
    responses = ResponseWriteSerializer(many=True, write_only=True)
    responses_detail = ResponseReadSerializer(many=True, read_only=True, source="responses")
    evaluator_first_name = serializers.CharField(source="evaluator.first_name", read_only=True)
    evaluator_last_name = serializers.CharField(source="evaluator.last_name", read_only=True)

    class Meta:
        model = Evaluation
        fields = [
            "id",
            "teacher_name",
            "college",
            "subject",
            "room_number",
            "date",
            "time_of_observation",
            "other_comments",
            "average_rating",
            "date_of_conference",
            "time_of_conference",
            "evaluator_first_name",
            "evaluator_last_name", 
            "responses",
            "responses_detail",
        ]


    def create(self, validated_data):
        responses_data = validated_data.pop("responses", [])
        evaluation = Evaluation.objects.create(**validated_data)
        total = 0
        count = 0

        for response_data in responses_data:
            rating = response_data.get("rating", 0)
            if rating and rating > 0:
                total += rating
                count += 1
            Response.objects.create(evaluation=evaluation, **response_data)

        if count > 0:
            evaluation.average_rating = total / count
            evaluation.save()

        return evaluation
