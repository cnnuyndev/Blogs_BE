#!/usr/bin/env python
"""
Test API registration endpoints
"""
import os
import sys
import django
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BE_BLOG.settings')
django.setup()

User = get_user_model()


class RegistrationAPITestCase(TestCase):
    """Test cases for registration API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.register_url = reverse('register_user')
        self.verify_url = reverse('verify_email')
        self.resend_url = reverse('resend_verification_email')

        self.valid_user_data = {
            "username": "testuser123",
            "email": "test@examplegmail.com",
            "password": "TestPass123",
            "first_name": "Test",
            "last_name": "User"
        }

    def test_user_registration_success(self):
        """Test successful user registration"""
        response = self.client.post(
            self.register_url, self.valid_user_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('id', response.data)
        self.assertIn('username', response.data)
        self.assertIn('email', response.data)

        # Check if user was created in database
        user = User.objects.get(username=self.valid_user_data['username'])
        self.assertEqual(user.email, self.valid_user_data['email'])
        # User should be inactive until email verification
        self.assertFalse(user.is_active)

    def test_user_registration_duplicate_username(self):
        """Test registration with duplicate username"""
        # Create first user
        self.client.post(self.register_url,
                         self.valid_user_data, format='json')

        # Try to create second user with same username
        duplicate_data = self.valid_user_data.copy()
        duplicate_data['email'] = 'another@example.com'

        response = self.client.post(
            self.register_url, duplicate_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        # Create first user
        self.client.post(self.register_url,
                         self.valid_user_data, format='json')

        # Try to create second user with same email
        duplicate_data = self.valid_user_data.copy()
        duplicate_data['username'] = 'anotheruser'

        response = self.client.post(
            self.register_url, duplicate_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_registration_invalid_password(self):
        """Test registration with invalid password"""
        invalid_data = self.valid_user_data.copy()
        invalid_data['password'] = 'weak'  # Too short

        response = self.client.post(
            self.register_url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_user_registration_missing_fields(self):
        """Test registration with missing required fields"""
        incomplete_data = {
            "username": "testuser",
            "email": "test@example.com"
            # Missing password
        }

        response = self.client.post(
            self.register_url, incomplete_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_resend_verification_email_success(self):
        """Test successful resend verification email"""
        # First register a user
        self.client.post(self.register_url,
                         self.valid_user_data, format='json')

        # Try to resend verification email
        resend_data = {"email": self.valid_user_data['email']}
        response = self.client.post(
            self.resend_url, resend_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_resend_verification_email_user_not_found(self):
        """Test resend verification email for non-existent user"""
        resend_data = {"email": "nonexistent@example.com"}
        response = self.client.post(
            self.resend_url, resend_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    def test_resend_verification_email_missing_email(self):
        """Test resend verification email without email"""
        response = self.client.post(self.resend_url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class EmailVerificationTestCase(TestCase):
    """Test cases for email verification"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.verify_url = reverse('verify_email')

        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPass123",
            is_active=False
        )

    def test_email_verification_missing_token(self):
        """Test email verification without token"""
        response = self.client.get(self.verify_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_email_verification_invalid_token(self):
        """Test email verification with invalid token"""
        response = self.client.get(f"{self.verify_url}?token=invalid_token")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


if __name__ == "__main__":
    # Run tests
    import unittest
    unittest.main()
