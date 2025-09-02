"""
Pytest configuration and fixtures
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from app.models import Blog

User = get_user_model()


@pytest.fixture
def api_client():
    """API client fixture"""
    return APIClient()


@pytest.fixture
def user():
    """Create a test user"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPass123',
        is_active=True
    )


@pytest.fixture
def inactive_user():
    """Create an inactive test user"""
    return User.objects.create_user(
        username='inactiveuser',
        email='inactive@example.com',
        password='TestPass123',
        is_active=False
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Authenticated API client"""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def blog_data():
    """Sample blog data"""
    return {
        'title': 'Test Blog Post',
        'content': 'This is a test blog post content.',
        'category': 'Backend'
    }


@pytest.fixture
def blog(user, blog_data):
    """Create a test blog"""
    return Blog.objects.create(
        title=blog_data['title'],
        content=blog_data['content'],
        category=blog_data['category'],
        author=user
    )


@pytest.fixture
def registration_data():
    """Sample registration data"""
    return {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'TestPass123',
        'first_name': 'New',
        'last_name': 'User'
    }
