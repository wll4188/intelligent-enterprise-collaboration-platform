from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if not username or not password:
        return Response({"detail": "用户名和密码必填"}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=username).exists():
        return Response({"detail": "用户名已存在"}, status=status.HTTP_400_BAD_REQUEST)
    User.objects.create_user(username=username, password=password)
    return Response({"detail": "注册成功"})


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response({"detail": "用户名或密码错误"}, status=status.HTTP_400_BAD_REQUEST)
    refresh = RefreshToken.for_user(user)
    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {"id": user.id, "username": user.username}
    })


@api_view(["POST"])
@permission_classes([AllowAny])
def refresh(request):
    token = request.data.get("refresh")
    if not token:
        return Response({"detail": "缺少 refresh token"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        refresh = RefreshToken(token)
        access = str(refresh.access_token)
        return Response({"access": access})
    except TokenError:
        return Response({"detail": "无效的 refresh token"}, status=status.HTTP_400_BAD_REQUEST)