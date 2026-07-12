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
    LoginResponseSerializer, TokenResponseSerializer,
    ChangePasswordSerializer, ChangePasswordResponseSerializer,
    UpdateProfileSerializer
)
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from apps.user_management.services.user_service import UserService

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

    @extend_schema(responses={200: UserSerializer})
    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=UpdateProfileSerializer,
        responses={200: UserSerializer},
        examples=[
            OpenApiExample(
                'Request',
                value={
                  "first_name": "Muskan",
                  "last_name": "Kumar",
                  "email": "muskan@example.com",
                  "username": "muskankumar"
                },
                request_only=True
            ),
            OpenApiExample(
                'Forbidden Field Error',
                value={
                  "detail": "Only first_name, last_name, email and username can be updated. Forbidden fields: groups."
                },
                response_only=True,
                status_codes=[str(status.HTTP_400_BAD_REQUEST)]
            )
        ]
    )
    def patch(self, request, *args, **kwargs):
        serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        
        try:
            UserService.create_audit_log(
                actor=request.user,
                target_user=request.user,
                action='profile_updated',
                description=f"User '{request.user.username}' updated their profile."
            )
        except Exception:
            pass

        # Return the full user object via UserSerializer so frontend has updated view
        response_serializer = UserSerializer(request.user)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

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

class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={200: ChangePasswordResponseSerializer},
        examples=[
            OpenApiExample(
                'Request',
                value={
                    "old_password": "OldPassword123!",
                    "new_password": "NewPassword123!"
                },
                request_only=True
            ),
            OpenApiExample(
                'Success',
                value={
                    "success": True,
                    "message": "Password changed successfully."
                },
                response_only=True,
                status_codes=[str(status.HTTP_200_OK)]
            ),
            OpenApiExample(
                'Wrong Password',
                value={
                    "old_password": [
                        "Old password is incorrect."
                    ]
                },
                response_only=True,
                status_codes=[str(status.HTTP_400_BAD_REQUEST)]
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        user = request.user

        if not user.check_password(old_password):
            return Response(
                {"old_password": ["Old password is incorrect."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        if old_password == new_password:
            return Response(
                {"new_password": ["New password must be different from old password."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as e:
            return Response(
                {"new_password": list(e.messages)},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        try:
            UserService.create_audit_log(
                actor=user,
                target_user=user,
                action='password_changed',
                description=f"User '{user.username}' changed their own password."
            )
        except Exception:
            pass

        return Response(
            {"success": True, "message": "Password changed successfully."},
            status=status.HTTP_200_OK
        )
