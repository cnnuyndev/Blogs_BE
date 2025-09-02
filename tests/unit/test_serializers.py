#!/usr/bin/env python
"""
Test serializers
"""
import os
import django
from django.test import TestCase
from django.contrib.auth import get_user_model
from app.serializers import (
    UserRegistrationSerializer,
    UserInfoSerializer,
    UpdateUserProfileSerializer,
    BlogSerializer
)
from app.models import Blog

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BE_BLOG.settings')
django.setup()

User = get_user_model()


class UserRegistrationSerializerTestCase(TestCase):
    """Test cases for UserRegistrationSerializer"""
    
    def setUp(self):
        """Set up test data"""
        self.valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_valid_registration_data(self):
        """Test valid registration data"""
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
    
    def test_invalid_password_too_short(self):
        """Test password validation - too short"""
        invalid_data = self.valid_data.copy()
        invalid_data['password'] = 'weak'
        
        serializer = UserRegistrationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_invalid_password_no_uppercase(self):
        """Test password validation - no uppercase"""
        invalid_data = self.valid_data.copy()
        invalid_data['password'] = 'testpass123'
        
        serializer = UserRegistrationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_invalid_password_no_lowercase(self):
        """Test password validation - no lowercase"""
        invalid_data = self.valid_data.copy()
        invalid_data['password'] = 'TESTPASS123'
        
        serializer = UserRegistrationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_invalid_password_no_number(self):
        """Test password validation - no number"""
        invalid_data = self.valid_data.copy()
        invalid_data['password'] = 'TestPass'
        
        serializer = UserRegistrationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_duplicate_email_validation(self):
        """Test duplicate email validation"""
        # Create a user first
        User.objects.create_user(
            username='existinguser',
            email='test@example.com',
            password='TestPass123'
        )
        
        # Try to register with same email
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_create_user(self):
        """Test user creation through serializer"""
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        
        self.assertEqual(user.username, self.valid_data['username'])
        self.assertEqual(user.email, self.valid_data['email'])
        self.assertEqual(user.first_name, self.valid_data['first_name'])
        self.assertEqual(user.last_name, self.valid_data['last_name'])
        self.assertFalse(user.is_active)  # Should be inactive until email verification
        self.assertTrue(user.check_password(self.valid_data['password']))


class UserInfoSerializerTestCase(TestCase):
    """Test cases for UserInfoSerializer"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_info_serialization(self):
        """Test user info serialization"""
        serializer = UserInfoSerializer(self.user)
        data = serializer.data
        
        self.assertEqual(data['username'], self.user.username)
        self.assertEqual(data['email'], self.user.email)
        self.assertEqual(data['first_name'], self.user.first_name)
        self.assertEqual(data['last_name'], self.user.last_name)
        self.assertIn('profile_picture', data)
        self.assertIn('bio', data)
        self.assertIn('job_title', data)
        self.assertIn('social_links', data)


class UpdateUserProfileSerializerTestCase(TestCase):
    """Test cases for UpdateUserProfileSerializer"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )
    
    def test_update_user_profile(self):
        """Test updating user profile"""
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'Updated bio',
            'job_title': 'Developer'
        }
        
        serializer = UpdateUserProfileSerializer(self.user, data=update_data)
        self.assertTrue(serializer.is_valid())
        
        updated_user = serializer.save()
        
        self.assertEqual(updated_user.first_name, update_data['first_name'])
        self.assertEqual(updated_user.last_name, update_data['last_name'])
        self.assertEqual(updated_user.bio, update_data['bio'])
        self.assertEqual(updated_user.job_title, update_data['job_title'])


class BlogSerializerTestCase(TestCase):
    """Test cases for BlogSerializer"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )
        
        self.blog_data = {
            'title': 'Test Blog Post',
            'content': 'This is a test blog post content.',
            'category': 'Backend'
        }
    
    def test_create_blog(self):
        """Test creating a blog through serializer"""
        serializer = BlogSerializer(data=self.blog_data)
        self.assertTrue(serializer.is_valid())
        
        blog = serializer.save(author=self.user)
        
        self.assertEqual(blog.title, self.blog_data['title'])
        self.assertEqual(blog.content, self.blog_data['content'])
        self.assertEqual(blog.category, self.blog_data['category'])
        self.assertEqual(blog.author, self.user)
        self.assertIsNotNone(blog.slug)
    
    def test_blog_serialization(self):
        """Test blog serialization"""
        blog = Blog.objects.create(
            title='Test Blog',
            content='Test content',
            category='Frontend',
            author=self.user
        )
        
        serializer = BlogSerializer(blog)
        data = serializer.data
        
        self.assertEqual(data['title'], blog.title)
        self.assertEqual(data['content'], blog.content)
        self.assertEqual(data['category'], blog.category)
        self.assertEqual(data['slug'], blog.slug)
        self.assertIn('author', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
    
    def test_invalid_category(self):
        """Test invalid category validation"""
        invalid_data = self.blog_data.copy()
        invalid_data['category'] = 'InvalidCategory'
        
        serializer = BlogSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('category', serializer.errors)
    
    def test_missing_required_fields(self):
        """Test missing required fields"""
        incomplete_data = {
            'title': 'Test Blog'
            # Missing content and category
        }
        
        serializer = BlogSerializer(data=incomplete_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('content', serializer.errors)
        self.assertIn('category', serializer.errors)


if __name__ == "__main__":
    # Run tests
    import unittest
    unittest.main()
