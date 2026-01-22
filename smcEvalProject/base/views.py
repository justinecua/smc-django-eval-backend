import bcrypt
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .serializer import UserSerializer

User = get_user_model()

@api_view(["POST"])
def login_view(request):
    print("🔥 HIT CUSTOM LOGIN VIEW 🔥", request.data)
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Username and password are required"}, status=400)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=400)

    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        return Response({"error": "Incorrect password"}, status=400)

    tokens = RefreshToken.for_user(user)
    return Response({
        "refresh": str(tokens),
        "access": str(tokens.access_token),
        "user": UserSerializer(user).data,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile_view(request):
    return Response(UserSerializer(request.user).data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=400)

        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response({"success": "Logged out successfully"}, status=200)

    except TokenError:
        return Response({"error": "Invalid or expired token"}, status=400)
