from dj_rest_auth.serializers import PasswordResetSerializer
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class CustomPasswordResetSerializer(PasswordResetSerializer):
    class Meta:
        model = User  # Use your custom user model

    def validate_email(self, value):
        """
        Ensure the email exists in the system.
        """
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value

    def save(self):
        """
        Override save to send an email with a password reset link.
        """
        request = self.context.get("request")
        email = self.validated_data["email"]
        user = User.objects.get(email=email)

        # Generate reset token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Construct the reset password link for the frontend
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"

        # Send email
        subject = "Reset Your Password"
        message = f"Click the link below to reset your password:\n\n{reset_link}"
        user.email_user(subject, message)

        return {"message": "Password reset link has been sent to your email.", "reset_link": reset_link}


class GoogleAuthSerializer(serializers.Serializer):
    provider = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
