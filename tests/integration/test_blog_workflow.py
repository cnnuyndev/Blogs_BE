#!/usr/bin/env python
"""
Integration tests for blog workflow
"""
import os
import django
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from app.models import Blog

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BE_BLOG.settings')
django.setup()

User = get_user_model()


class BlogWorkflowTestCase(TestCase):
    """Integration tests for complete blog workflow"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123',
            is_active=True
        )
        
        # Authenticate user
        self.client.force_authenticate(user=self.user)
        
        # Blog data
        self.blog_data = {
            'title': 'Test Blog Post',
            'content': 'This is a test blog post content.',
            'category': 'Backend'
        }
    
    def test_complete_blog_workflow(self):
        """Test complete blog workflow: create, read, update, delete"""
        
        # 1. Create blog
        create_response = self.client.post(
            reverse('create_blog'),
            self.blog_data,
            format='json'
        )
        
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        blog_id = create_response.data['id']
        blog_slug = create_response.data['slug']
        
        # 2. Read blog list
        list_response = self.client.get(reverse('blog_list'))
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertIn('results', list_response.data)
        self.assertEqual(len(list_response.data['results']), 1)
        
        # 3. Read specific blog
        detail_response = self.client.get(
            reverse('get_blog', kwargs={'slug': blog_slug})
        )
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data['title'], self.blog_data['title'])
        
        # 4. Update blog
        update_data = self.blog_data.copy()
        update_data['title'] = 'Updated Blog Post'
        update_data['content'] = 'Updated content'
        
        update_response = self.client.put(
            reverse('update_blog', kwargs={'pk': blog_id}),
            update_data,
            format='json'
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['title'], update_data['title'])
        
        # 5. Delete blog
        delete_response = self.client.post(
            reverse('delete_blog', kwargs={'pk': blog_id})
        )
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 6. Verify blog is deleted
        list_response_after_delete = self.client.get(reverse('blog_list'))
        self.assertEqual(len(list_response_after_delete.data['results']), 0)
    
    def test_blog_authorization(self):
        """Test blog authorization - only author can edit/delete"""
        
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='TestPass123',
            is_active=True
        )
        
        # Create blog with first user
        create_response = self.client.post(
            reverse('create_blog'),
            self.blog_data,
            format='json'
        )
        blog_id = create_response.data['id']
        
        # Try to update with other user
        self.client.force_authenticate(user=other_user)
        update_response = self.client.put(
            reverse('update_blog', kwargs={'pk': blog_id}),
            self.blog_data,
            format='json'
        )
        self.assertEqual(update_response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try to delete with other user
        delete_response = self.client.post(
            reverse('delete_blog', kwargs={'pk': blog_id})
        )
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_blog_pagination(self):
        """Test blog list pagination"""
        
        # Create multiple blogs
        for i in range(5):
            blog_data = self.blog_data.copy()
            blog_data['title'] = f'Blog Post {i+1}'
            self.client.post(
                reverse('create_blog'),
                blog_data,
                format='json'
            )
        
        # Test pagination
        response = self.client.get(reverse('blog_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        
        # Check page size (should be 3 as configured)
        self.assertEqual(len(response.data['results']), 3)
        self.assertEqual(response.data['count'], 5)
    
    def test_blog_cache_invalidation(self):
        """Test that cache is invalidated when blog is updated/deleted"""
        
        # Create blog
        create_response = self.client.post(
            reverse('create_blog'),
            self.blog_data,
            format='json'
        )
        blog_slug = create_response.data['slug']
        
        # Get blog (should cache)
        first_response = self.client.get(
            reverse('get_blog', kwargs={'slug': blog_slug})
        )
        
        # Update blog
        update_data = self.blog_data.copy()
        update_data['title'] = 'Updated Title'
        self.client.put(
            reverse('update_blog', kwargs={'pk': create_response.data['id']}),
            update_data,
            format='json'
        )
        
        # Get blog again (should show updated data)
        second_response = self.client.get(
            reverse('get_blog', kwargs={'slug': blog_slug})
        )
        
        self.assertEqual(second_response.data['title'], 'Updated Title')


class UserWorkflowTestCase(TestCase):
    """Integration tests for user workflow"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123',
            is_active=True
        )
        
        # Authenticate user
        self.client.force_authenticate(user=self.user)
    
    def test_user_profile_workflow(self):
        """Test user profile workflow"""
        
        # 1. Get user info
        userinfo_response = self.client.get(
            reverse('get_userinfo', kwargs={'username': self.user.username})
        )
        self.assertEqual(userinfo_response.status_code, status.HTTP_200_OK)
        self.assertEqual(userinfo_response.data['username'], self.user.username)
        
        # 2. Get current username
        username_response = self.client.get(reverse('get_username'))
        self.assertEqual(username_response.status_code, status.HTTP_200_OK)
        self.assertEqual(username_response.data['username'], self.user.username)
        
        # 3. Update profile
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'Updated bio',
            'job_title': 'Developer'
        }
        
        update_response = self.client.put(
            reverse('update_user'),
            update_data,
            format='json'
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['first_name'], update_data['first_name'])
        
        # 4. Verify profile is updated
        updated_userinfo_response = self.client.get(
            reverse('get_userinfo', kwargs={'username': self.user.username})
        )
        self.assertEqual(updated_userinfo_response.data['bio'], update_data['bio'])


if __name__ == "__main__":
    # Run tests
    import unittest
    unittest.main()
