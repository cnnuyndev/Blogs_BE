from rest_framework import serializers
from .models import Blog
from django.contrib.auth import get_user_model
import re


class SimpleAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username", "first_name",
                  "last_name", "email", "profile_picture"]


class BlogSerializer(serializers.ModelSerializer):
    author = SimpleAuthorSerializer(read_only=True)

    class Meta:
        model = Blog
        fields = ['id', 'title', 'slug', 'author', 'category', 'content',
                  'featured_image', 'published_date', 'created_at', 'updated_at', 'is_draft']


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = get_user_model()
        fields = ["id", "username", "email",
                  "first_name", "last_name", "password"]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        User = get_user_model()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email đã được sử dụng.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Mật khẩu phải có ít nhất 8 ký tự.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError(
                "Mật khẩu phải chứa ít nhất 1 chữ hoa.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError(
                "Mật khẩu phải chứa ít nhất 1 chữ thường.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError(
                "Mật khẩu phải chứa ít nhất 1 số.")
        return value

    def create(self, validated_data):
        User = get_user_model()
        new_user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_active=False,
        )
        new_user.set_password(validated_data['password'])
        new_user.save()
        return new_user


class UserInfoSerializer(serializers.ModelSerializer):
    author_posts = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ["id", "username", "email", "first_name", "last_name",
                  "job_title", "bio", "profile_picture", "author_posts"]

    def get_author_posts(self, user):
        blogs = Blog.objects.filter(author=user)[:6]
        serializer = BlogSerializer(blogs, many=True)
        return serializer.data


class UpdateUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "email", "username", "first_name", "last_name", "bio", "job_title", "profile_picture",
                  "facebook", "youtube", "instagram", "twitter"]
