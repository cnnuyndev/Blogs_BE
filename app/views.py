from rest_framework.decorators import api_view, permission_classes, throttle_classes
import logging
from .models import Blog
from .serializers import BlogSerializer, UserRegistrationSerializer, UserInfoSerializer, UpdateUserProfileSerializer
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.core import signing
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.throttling import AnonRateThrottle
from django.template.loader import render_to_string
from django.core.cache import cache  # Cache backend (Redis qua django-redis)

logger = logging.getLogger(__name__)


class BlogListPagination(PageNumberPagination):
    page_size = 3


@api_view(["GET"])
def blog_list(request):
    # Cache key dựa trên full URL (bao gồm query string: trang, filter, ...)
    cache_key = f"blog_list:{request.get_full_path()}"
    cached_payload = cache.get(cache_key)
    if cached_payload is not None:
        print("cache key: ", cache_key)
        print("cache: ", cached_payload)
        # Trả về payload đã cache (bao gồm cả cấu trúc pagination của DRF)
        return Response(cached_payload)

    # Không có cache: truy vấn DB, phân trang, serialize
    blogs = Blog.objects.all()
    paginator = BlogListPagination()
    paginated_blogs = paginator.paginate_queryset(blogs, request)
    serializer = BlogSerializer(paginated_blogs, many=True)

    # DRF pagination trả Response đặc biệt; ta cache phần data của Response
    paginated_response = paginator.get_paginated_response(serializer.data)
    payload = paginated_response.data

    # Lưu cache trong 15 phút (tuỳ chỉnh theo nhu cầu)
    cache.set(cache_key, payload, timeout=60*15)
    return Response(payload)


@api_view(["GET"])
def get_blog(request, slug):
    # Cache theo slug bài viết
    cache_key = f"blog_detail:{slug}"
    cached = cache.get(cache_key)
    if cached is not None:
        return Response(cached)

    try:
        blog = Blog.objects.get(slug=slug)
        serializer = BlogSerializer(blog)
        data = serializer.data
        cache.set(cache_key, data, timeout=60*15)  # Cache 15 phút
        return Response(data)
    except Blog.DoesNotExist:
        return Response({"error": "Blog not found"}, status=404)


# Hàm tiện ích để xoá cache liên quan đến blog list/detail
def invalidate_blog_cache(slug: str | None = None) -> None:
    try:
        # Xoá cache list (mọi trang/param) — pattern match nếu backend hỗ trợ
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern('blog_list:*')
        else:
            # Fallback an toàn nếu không hỗ trợ pattern
            cache.clear()
    except Exception:
        cache.clear()

    if slug:
        cache.delete(f"blog_detail:{slug}")


class RegistrationRateThrottle(AnonRateThrottle):
    rate = '5/hour'


@api_view(["POST"])
@throttle_classes([RegistrationRateThrottle])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Tạo token xác thực email
        token_data = {
            "user_id": user.id,
            "email": user.email
        }
        token = signing.dumps(token_data, salt="email-verify")

        # Tạo URL xác thực
        verify_url = request.build_absolute_uri(
            f"/api/verify-email/?token={token}")

        # Chuẩn bị nội dung email
        context = {
            'user': user,
            'verify_url': verify_url,
            'site_name': 'DevScribe Blogs'
        }

        # Render email template
        html_message = render_to_string(
            '../templates/email/verification_email.html', context)
        plain_message = render_to_string(
            '../templates/email/verification_email.txt', context)

        subject = f"{settings.EMAIL_SUBJECT_PREFIX}Xác thực email đăng ký tài khoản"

        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False
            )
        except Exception as e:
            logger.error(
                f"Failed to send verification email to {user.email}: {str(e)}")
            # Có thể xử lý thêm như xóa user nếu không gửi được email

        return Response({
            "message": "Đăng ký thành công. Vui lòng kiểm tra email để xác thực và kích hoạt tài khoản.",
            "id": user.id,
            "username": user.username,
            "email": user.email
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_userinfo(request, username):
    User = get_user_model()
    user = User.objects.get(username=username)
    serializer = UserInfoSerializer(user)
    return Response(serializer.data)


@api_view(["GET"])
def verify_email(request):
    token = request.GET.get("token")
    if not token:
        return Response({"error": "Thiếu token"}, status=status.HTTP_400_BAD_REQUEST)

    User = get_user_model()
    try:
        # Giải mã token
        data = signing.loads(
            token,
            salt="email-verify",
            max_age=settings.EMAIL_VERIFICATION_TIMEOUT
        )

        # Kiểm tra dữ liệu token
        if "user_id" not in data or "email" not in data:
            return Response(
                {"error": "Token không hợp lệ"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Lấy và kiểm tra user
        user = User.objects.get(id=data["user_id"], email=data["email"])

        if user.is_active:
            return Response({"message": "Tài khoản đã được kích hoạt trước đó."})

        user.is_active = True
        user.save(update_fields=["is_active"])

        return Response({
            "message": "Xác thực email thành công. Tài khoản đã được kích hoạt."
        })

    except User.DoesNotExist:
        return Response(
            {"error": "Người dùng không tồn tại"},
            status=status.HTTP_404_NOT_FOUND
        )
    except signing.SignatureExpired:
        return Response(
            {"error": "Token đã hết hạn"},
            status=status.HTTP_400_BAD_REQUEST
        )
    except signing.BadSignature:
        return Response(
            {"error": "Token không hợp lệ"},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Email verification error: {str(e)}")
        return Response(
            {"error": "Đã có lỗi xảy ra"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_username(request):
    print('aaaa')
    user = request.user
    username = user.username
    print(username)
    return Response({"username": username})


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    user = request.user
    serializer = UpdateUserProfileSerializer(user, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POSt'])
@permission_classes([IsAuthenticated])
def create_blog(request):
    user = request.user
    serializer = BlogSerializer(data=request.data)
    if serializer.is_valid():
        blog = serializer.save(author=user)
        # Invalidate cache sau khi tạo blog mới để list/detail phản ánh dữ liệu mới
        invalidate_blog_cache(slug=getattr(blog, 'slug', None))
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_blog(request, pk):
    user = request.user
    blog = Blog.objects.get(id=pk)
    if blog.author != user:
        return Response({"error": "You are not the author of this blog"}, status=status.HTTP_403_FORBIDDEN)
    old_slug = getattr(blog, 'slug', None)
    serializer = BlogSerializer(blog, data=request.data)
    if serializer.is_valid():
        blog = serializer.save()
        # Invalidate cache sau khi cập nhật; xử lý cả trường hợp slug thay đổi
        new_slug = getattr(blog, 'slug', None)
        invalidate_blog_cache(slug=old_slug)
        if new_slug and new_slug != old_slug:
            invalidate_blog_cache(slug=new_slug)
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_blog(request, pk):
    blog = Blog.objects.get(id=pk)
    user = request.user
    if blog.author != user:
        return Response({"error": "You are not the author of this blog"}, status=status.HTTP_403_FORBIDDEN)
    slug = getattr(blog, 'slug', None)
    blog.delete()
    # Invalidate cache sau khi xoá
    invalidate_blog_cache(slug=slug)
    return Response({"message": "Blog deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
