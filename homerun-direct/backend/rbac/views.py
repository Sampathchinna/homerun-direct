from .serializers import CustomPasswordResetSerializer, GoogleAuthSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from core.viewsets import  GenericResponseMixin
from rest_framework.permissions import AllowAny
from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings
from rest_framework import viewsets
import requests
from django.contrib.auth.hashers import make_password
from organization.models import *


User = get_user_model()


def store_user_entities_in_session(user, session):
    organization_ids = list(
        Organization.objects.filter(user=user).values_list("id", flat=True)
    )
    brand_ids = list(
        Brand.objects.filter(organization__user=user).values_list("id", flat=True)
    )
    session["organization_ids"] = organization_ids
    session["brand_ids"] = brand_ids
    session.modified = True

class CustomLoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        print("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD")
        if not user:
            # If user not found locally, call legacy system
            if not User.objects.filter(username=username).exists():
                payload = {"email": username, "password": password}
                try:
                    #{'email': 'cody+fleet@rvshare.com', 'password': 'P@ss@r123'}
                    response = requests.post(
                        settings.CURRENT_DIRECT_LOGIN_URL,
                        json=payload,
                        timeout=5
                    )
                    if response.status_code == 200:
                        # Create user locally and save hashed password
                        user = User.objects.create(
                            username=username,
                            email=username,
                            password=make_password(password)
                        )
                        user.save()
                        user = authenticate(username=username, password=password)
                except requests.RequestException:
                    return Response(
                        {"detail": "Legacy authentication service unavailable."},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE
                    )

        if user and user.is_authenticated:
            if not user.is_superuser:
                store_user_entities_in_session(user, request.session)
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            # ✅ Ensure "access_token" is inside "data"
            return Response(
                {
                    "access_token": access_token,
                    "refresh_token": str(refresh),
                    "username": user.username,
                    "userId": user.id,
                    "phone_number": getattr(user, "phone_number", None),
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"detail": "Invalid username or password"},
            status=status.HTTP_400_BAD_REQUEST,
        )





class CustomPasswordResetView(GenericResponseMixin, PasswordResetView):
    """
    API for requesting password reset.
    """

    permission_classes = [AllowAny]
    serializer_class = CustomPasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reset_data = serializer.save()

        return self.format_success_response(
            message="A password reset link has been sent to your email.",
            data={
                "email": request.data.get("email"),
                  "reset_link": reset_data["reset_link"]
            },
            status_code=200,
        )


class CustomPasswordResetConfirmView(GenericResponseMixin, PasswordResetConfirmView):
    """
    API for confirming password reset.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        uidb64 = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        print(f"✅ Received UID (Base64): {uidb64}")
        print(f"✅ Received Token: {token}")

        if not uidb64 or not token or not new_password:
            return self.format_error_response(
                errors={"fields": "UID, token, and new_password are required"},
                message="Invalid password reset request",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Decode UID from Base64
            decoded_uid = force_str(urlsafe_base64_decode(uidb64))
            print(f"� Decoded UID: {decoded_uid}")

            # Fetch the user
            user = User.objects.filter(pk=decoded_uid).first()
            if not user:
                print("❌ User not found for UID!")
                return self.format_error_response(
                    errors={"uid": "Invalid value"},
                    message="Invalid password reset request",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # 🔥 Check token validity
            if not default_token_generator.check_token(user, token):
                print("❌ Invalid or expired token!")
                return self.format_error_response(
                    errors={"detail": "Invalid or expired token"},
                    message="Token verification failed",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # ✅ Set new password
            user.set_password(new_password)
            user.save()
            print("✅ Password updated successfully!")

            # 🔥 FIXED: Pass `data` as an empty dictionary `{}` to `format_success_response()`
            return self.format_success_response(
                data={},  # FIX: Pass empty data instead of skipping the argument
                message="Your password has been successfully reset.",
                status_code=status.HTTP_200_OK,
            )

        except Exception as e:
            print(f"❌ Decoding Error: {e}")
            return self.format_error_response(
                errors={"uid": "Invalid value"},
                message="Invalid password reset request",
                status_code=status.HTTP_400_BAD_REQUEST,
            )


class GoogleAuthViewSet(viewsets.GenericViewSet):
    """Handles Google authentication using a ModelViewSet approach."""

    permission_classes = [AllowAny]
    serializer_class = GoogleAuthSerializer  # ✅ Define serializer_class

    def create(self, request):
        """POST request for Google authentication"""
        print("Google Authentication data user save")
        serializer = self.get_serializer(
            data=request.data
        )  # ✅ Fix: Now get_serializer() works
        serializer.is_valid(raise_exception=True)

        provider = serializer.validated_data.get("provider")
        access_token = serializer.validated_data.get("token")

        if provider != "google" or not access_token:
            return Response(
                {"error": "Invalid provider or missing token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Verify Google ID Token
            id_info = id_token.verify_oauth2_token(
                access_token,
                google_requests.Request(),
                audience=None,
            )

            email = id_info.get("email")
            name = id_info.get("name")

            if not email:
                return Response(
                    {"error": "Google account must have an email"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if user exists, otherwise create one
            user, created = User.objects.get_or_create(
                email=email, defaults={"username": email, "name": name}
            )

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response(
                {
                    "message": "User authenticated successfully",
                    "email": user.email,
                    "name": user.name,
                    "is_new_user": created,
                    "access_token": access_token,
                    "refresh_token": str(refresh),
                    "username": user.username,
                    "userId": user.id,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)