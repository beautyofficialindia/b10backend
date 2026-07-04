from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiExample
from .serializers import (
    CustomTokenObtainPairSerializer, UserSerializer,
    LogoutRequestSerializer, RefreshRequestSerializer,
    LoginResponseSerializer, TokenResponseSerializer
)

class LoginAPIView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        responses={200: LoginResponseSerializer},
        examples=[
            OpenApiExample(
                'Valid Login',
                value={
                    "username": "admin",
                    "password": "password"
                },
                request_only=True,
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LogoutRequestSerializer,
        examples=[
            OpenApiExample(
                'Valid Logout',
                value={"refresh": "refresh-token"},
                request_only=True
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RefreshAPIView(TokenRefreshView):
    @extend_schema(
        request=RefreshRequestSerializer,
        responses={200: TokenResponseSerializer},
        examples=[
            OpenApiExample(
                'Valid Refresh',
                value={"refresh": "refresh-token"},
                request_only=True
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
