#!/usr/bin/env python
"""
Test models
"""
import os
import django
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from app.models import Blog, CustomUser

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BE_BLOG.settings')
django.setup()

User = get_user_model()


class CustomUserModelTestCase(TestCase):
    """Test cases for CustomUser model"""
    
    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_create_user(self):
        """Test creating a user"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.first_name, self.user_data['first_name'])
        self.assertEqual(user.last_name, self.user_data['last_name'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='AdminPass123'
        )
        
        self.assertEqual(superuser.username, 'admin')
        self.assertEqual(superuser.email, 'admin@example.com')
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
    
    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), self.user_data['username'])
    
    def test_user_email_unique(self):
        """Test that email must be unique"""
        User.objects.create_user(**self.user_data)
        
        # Try to create another user with same email
        duplicate_data = self.user_data.copy()
        duplicate_data['username'] = 'anotheruser'
        
        with self.assertRaises(Exception):  # Should raise IntegrityError
            User.objects.create_user(**duplicate_data)
    
    def test_user_username_unique(self):
        """Test that username must be unique"""
        User.objects.create_user(**self.user_data)
        
        # Try to create another user with same username
        duplicate_data = self.user_data.copy()
        duplicate_data['email'] = 'another@example.com'
        
        with self.assertRaises(Exception):  # Should raise IntegrityError
            User.objects.create_user(**duplicate_data)


class BlogModelTestCase(TestCase):
    """Test cases for Blog model"""
    
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
            'category': 'Backend',
            'author': self.user
        }
    
    def test_create_blog(self):
        """Test creating a blog post"""
        blog = Blog.objects.create(**self.blog_data)
        
        self.assertEqual(blog.title, self.blog_data['title'])
        self.assertEqual(blog.content, self.blog_data['content'])
        self.assertEqual(blog.category, self.blog_data['category'])
        self.assertEqual(blog.author, self.user)
        self.assertIsNotNone(blog.slug)
        self.assertIsNotNone(blog.created_at)
        self.assertIsNotNone(blog.updated_at)
    
    def test_blog_str_representation(self):
        """Test blog string representation"""
        blog = Blog.objects.create(**self.blog_data)
        self.assertEqual(str(blog), self.blog_data['title'])
    
    def test_blog_slug_generation(self):
        """Test automatic slug generation"""
        blog = Blog.objects.create(**self.blog_data)
        
        # Slug should be generated from title
        expected_slug = 'test-blog-post'
        self.assertEqual(blog.slug, expected_slug)
    
    def test_blog_slug_unique(self):
        """Test that slug must be unique"""
        Blog.objects.create(**self.blog_data)
        
        # Try to create another blog with same title (should generate same slug)
        duplicate_data = self.blog_data.copy()
        duplicate_data['content'] = 'Different content'
        
        with self.assertRaises(Exception):  # Should raise IntegrityError
            Blog.objects.create(**duplicate_data)
    
    def test_blog_category_choices(self):
        """Test blog category choices"""
        valid_categories = ['Frontend', 'Backend', 'Fullstack', 'Design', 'Blockchain', 'DevOps', 'AI', 'Other']
        
        for category in valid_categories:
            blog_data = self.blog_data.copy()
            blog_data['title'] = f'Test {category}'
            blog_data['category'] = category
            blog = Blog.objects.create(**blog_data)
            self.assertEqual(blog.category, category)
    
    def test_blog_author_relationship(self):
        """Test blog author relationship"""
        blog = Blog.objects.create(**self.blog_data)
        
        # Test forward relationship
        self.assertEqual(blog.author, self.user)
        
        # Test reverse relationship
        self.assertIn(blog, self.user.blog_set.all())
    
    def test_blog_ordering(self):
        """Test blog ordering (newest first)"""
        # Create multiple blogs
        blog1 = Blog.objects.create(**self.blog_data)
        
        blog2_data = self.blog_data.copy()
        blog2_data['title'] = 'Second Blog'
        blog2 = Blog.objects.create(**blog2_data)
        
        # Get all blogs
        blogs = Blog.objects.all()
        
        # Should be ordered by created_at descending (newest first)
        self.assertEqual(blogs[0], blog2)
        self.assertEqual(blogs[1], blog1)


if __name__ == "__main__":
    # Run tests
    import unittest
    unittest.main()
