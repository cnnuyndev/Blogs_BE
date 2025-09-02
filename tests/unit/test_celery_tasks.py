#!/usr/bin/env python
"""
Test Celery tasks
"""
import os
import django
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from app.tasks import (
    send_verification_email_task,
    send_notification_email_task,
    send_blog_notification_task,
    resend_verification_email_task,
    test_celery_connection_task
)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BE_BLOG.settings')
django.setup()

User = get_user_model()


class CeleryTasksTestCase(TestCase):
    """Test cases for Celery tasks"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPass123",
            is_active=False
        )
    
    def test_test_celery_connection_task(self):
        """Test Celery connection test task"""
        result = test_celery_connection_task()
        self.assertEqual(result, "Celery is working properly!")
    
    @patch('app.tasks.send_mail')
    def test_send_verification_email_task_success(self, mock_send_mail):
        """Test successful verification email task"""
        mock_send_mail.return_value = 1  # send_mail returns number of emails sent
        
        result = send_verification_email_task(
            subject="Test Subject",
            plain_message="Test message",
            html_message="<p>Test HTML</p>",
            to_email="test@example.com",
            from_email="noreply@example.com"
        )
        
        self.assertTrue(result)
        mock_send_mail.assert_called_once()
    
    @patch('app.tasks.send_mail')
    def test_send_verification_email_task_failure(self, mock_send_mail):
        """Test verification email task failure"""
        mock_send_mail.side_effect = Exception("SMTP error")
        
        # This should raise an exception for retry
        with self.assertRaises(Exception):
            send_verification_email_task(
                subject="Test Subject",
                plain_message="Test message",
                html_message="<p>Test HTML</p>",
                to_email="test@example.com",
                from_email="noreply@example.com"
            )
    
    @patch('app.tasks.send_mail')
    def test_send_notification_email_task_success(self, mock_send_mail):
        """Test successful notification email task"""
        mock_send_mail.return_value = 1
        
        result = send_notification_email_task(
            subject="Test Subject",
            message="Test message",
            to_email="test@example.com"
        )
        
        self.assertTrue(result)
        mock_send_mail.assert_called_once()
    
    @patch('app.tasks.send_mail')
    def test_send_blog_notification_task_success(self, mock_send_mail):
        """Test successful blog notification task"""
        mock_send_mail.return_value = 1
        
        result = send_blog_notification_task(
            blog_title="Test Blog",
            blog_author="Test Author",
            subscriber_emails=["test@example.com", "another@example.com"]
        )
        
        self.assertTrue(result)
        # Should be called twice (once for each email)
        self.assertEqual(mock_send_mail.call_count, 2)
    
    @patch('app.tasks.send_mail')
    @patch('app.tasks.render_to_string')
    @patch('app.tasks.signing.dumps')
    def test_resend_verification_email_task_success(self, mock_dumps, mock_render, mock_send_mail):
        """Test successful resend verification email task"""
        mock_dumps.return_value = "test_token"
        mock_render.side_effect = ["Test HTML", "Test Plain"]
        mock_send_mail.return_value = 1
        
        result = resend_verification_email_task(
            user_id=self.user.id,
            user_email=self.user.email
        )
        
        self.assertTrue(result)
        mock_send_mail.assert_called_once()
    
    def test_resend_verification_email_task_user_not_found(self):
        """Test resend verification email task with non-existent user"""
        result = resend_verification_email_task(
            user_id=99999,
            user_email="nonexistent@example.com"
        )
        
        self.assertFalse(result)
    
    def test_resend_verification_email_task_user_already_active(self):
        """Test resend verification email task with already active user"""
        self.user.is_active = True
        self.user.save()
        
        result = resend_verification_email_task(
            user_id=self.user.id,
            user_email=self.user.email
        )
        
        self.assertTrue(result)


if __name__ == "__main__":
    # Run tests
    import unittest
    unittest.main()
