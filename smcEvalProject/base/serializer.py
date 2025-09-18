from django.contrib.auth.models import User
from rest_framework import serializers
from .models import PersonnelInfo

class PersonnelInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonnelInfo
        fields = ["middle_name", "position", "employID"]

class UserSerializer(serializers.ModelSerializer):
    personnelinfo = PersonnelInfoSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email",
            "first_name", "last_name",
            "personnelinfo",
        ]
