from rest_framework import serializers
from .models import Blog
from django.contrib.auth import get_user_model


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
    class Meta:
        model = get_user_model()
        fields = ["id", "username", "first_name", "last_name", "password"]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user_name = validated_data['username']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        password = validated_data['password']

        user = get_user_model()
        new_user = user.objects.create(username=user_name,
                                       first_name=first_name, last_name=last_name)
        new_user.set_password(password)
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
