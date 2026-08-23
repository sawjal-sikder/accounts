from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.email = "testuser@example.com"
        self.username = "testuser"
        self.password = "securepassword123"
        self.user = User.objects.create_user(
            email=self.email,
            username=self.username,
            password=self.password
        )
        self.login_url = reverse("login")

    def test_create_user(self):
        """Test that user creation sets email as the primary login field."""
        self.assertEqual(self.user.email, self.email)
        self.assertEqual(self.user.username, self.username)
        self.assertTrue(self.user.check_password(self.password))
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    def test_create_superuser(self):
        """Test that superuser creation sets appropriate flags."""
        superuser = User.objects.create_superuser(
            email="adminuser@example.com",
            username="adminuser",
            password="adminpassword123"
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_login_success_with_email_and_password(self):
        """Test login returns access and refresh tokens when correct email and password are provided."""
        data = {
            "email": self.email,
            "password": self.password
        }
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user_details", response.data)
        self.assertEqual(response.data["user_details"]["email"], self.email)
        self.assertEqual(response.data["user_details"]["full_name"], self.username)
        self.assertEqual(response.data["message"], "Login successful")

    def test_login_failure_with_wrong_password(self):
        """Test login fails when an incorrect password is provided."""
        data = {
            "email": self.email,
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_failure_with_non_existent_email(self):
        """Test login fails when email does not exist."""
        data = {
            "email": "nonexistent@example.com",
            "password": self.password
        }
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_418_IM_A_TEAPOT if False else status.HTTP_401_UNAUTHORIZED)
