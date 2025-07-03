import pytest
from django.contrib.auth import get_user_model
from unittest.mock import patch
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from rest_framework.exceptions import ValidationError
from rbac.serializers import CustomPasswordResetSerializer
import pytest
from rest_framework.exceptions import ValidationError
from rbac.serializers import GoogleAuthSerializer


import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from unittest.mock import patch
from rest_framework.exceptions import ValidationError
from rbac.serializers import CustomPasswordResetSerializer

User = get_user_model()

@pytest.mark.django_db
class TestCustomPasswordResetSerializer:

    def setup_method(self):
        """Setup test dependencies"""
        self.factory = RequestFactory()  # ✅ Initialize request factory
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpassword")

    def test_validate_email_existing_user(self):
        """Test email validation for existing user"""
        serializer = CustomPasswordResetSerializer(data={"email": "test@example.com"})
        assert serializer.is_valid()  # ✅ Should pass validation

    def test_validate_email_non_existing_user(self):
        """Test email validation for non-existing user"""
        serializer = CustomPasswordResetSerializer(data={"email": "nonexistent@example.com"})

        with pytest.raises(ValidationError, match="No user found with this email address."):
            serializer.is_valid(raise_exception=True)

    @patch("django.core.mail.EmailMessage.send")  # ✅ Mock email sending
    def test_save_sends_reset_email(self, mock_send_email):
        """Test that password reset email is sent"""
        request = self.factory.post("/auth/password/reset/")  # ✅ Fix request factory usage
        data = {"email": "test@example.com"}

        serializer = CustomPasswordResetSerializer(data=data, context={'request': request})
        assert serializer.is_valid()  # ✅ Validate input

        response = serializer.save()  # ✅ Call save method

        assert "Password reset link has been sent" in response["message"]  # ✅ Check response
        assert mock_send_email.called  # ✅ Ensure email was sent








@pytest.mark.django_db
class TestGoogleAuthSerializer:

    def test_valid_google_auth_data(self):
        """Test valid GoogleAuthSerializer data"""
        data = {"provider": "google", "token": "valid_token"}
        serializer = GoogleAuthSerializer(data=data)
        assert serializer.is_valid()

    def test_missing_provider(self):
        """Test missing provider field"""
        data = {"token": "valid_token"}
        serializer = GoogleAuthSerializer(data=data)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_missing_token(self):
        """Test missing token field"""
        data = {"provider": "google"}
        serializer = GoogleAuthSerializer(data=data)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
