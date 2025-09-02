"""
Celery tasks cho app.
Chứa các tác vụ nền (background tasks) như gửi email, xử lý file, etc.
"""

import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.core import signing

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),  # Tự động retry khi có exception
    retry_backoff=60,  # Tăng thời gian chờ giữa các lần retry (60s, 120s, 240s...)
    retry_kwargs={"max_retries": 5},  # Tối đa 5 lần retry
    name="send_verification_email"  # Tên task để dễ debug
)
def send_verification_email_task(self, subject, plain_message, html_message, to_email, from_email):
    """
    Task gửi email xác thực tài khoản.
    
    Args:
        subject: Tiêu đề email
        plain_message: Nội dung text
        html_message: Nội dung HTML
        to_email: Email người nhận
        from_email: Email người gửi
    
    Returns:
        bool: True nếu gửi thành công, False nếu thất bại
    """
    try:
        # Gửi email sử dụng Django's send_mail
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False,  # Ném exception nếu lỗi để Celery có thể retry
        )
        logger.info(f"Email verification sent successfully to {to_email}")
        return True
        
    except Exception as exc:
        # Log lỗi và để Celery retry
        logger.error(f"Failed to send verification email to {to_email}: {str(exc)}")
        # Ném exception để trigger retry
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=30,
    retry_kwargs={"max_retries": 3},
    name="send_notification_email"
)
def send_notification_email_task(self, subject, message, to_email, from_email=None):
    """
    Task gửi email thông báo chung.
    
    Args:
        subject: Tiêu đề email
        message: Nội dung email (có thể là HTML)
        to_email: Email người nhận
        from_email: Email người gửi (mặc định từ settings)
    
    Returns:
        bool: True nếu gửi thành công
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
        
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[to_email],
            fail_silently=False,
        )
        logger.info(f"Notification email sent successfully to {to_email}")
        return True
        
    except Exception as exc:
        logger.error(f"Failed to send notification email to {to_email}: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(name="clear_expired_cache")
def clear_expired_cache_task():
    """
    Task dọn dẹp cache hết hạn (có thể chạy định kỳ).
    Hữu ích nếu cache backend không tự động cleanup.
    """
    try:
        # Django cache backend thường tự động cleanup, nhưng có thể cần manual
        # Đây là placeholder cho logic cleanup tùy chỉnh nếu cần
        logger.info("Cache cleanup task completed")
        return True
    except Exception as exc:
        logger.error(f"Cache cleanup failed: {str(exc)}")
        return False


@shared_task(name="test_celery_connection")
def test_celery_connection_task():
    """
    Task test để kiểm tra Celery worker hoạt động.
    Có thể gọi từ Django shell: test_celery_connection_task.delay()
    """
    logger.info("Celery connection test successful")
    return "Celery is working properly!"


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=60,
    retry_kwargs={"max_retries": 3},
    name="send_blog_notification"
)
def send_blog_notification_task(self, blog_title, blog_author, subscriber_emails):
    """
    Task gửi thông báo khi có blog mới (cho subscribers).
    
    Args:
        blog_title: Tiêu đề blog
        blog_author: Tác giả blog
        subscriber_emails: Danh sách email subscribers
    
    Returns:
        bool: True nếu gửi thành công
    """
    try:
        subject = f"{settings.EMAIL_SUBJECT_PREFIX}Blog mới: {blog_title}"
        message = f"""
        Blog mới đã được đăng bởi {blog_author}!
        
        Tiêu đề: {blog_title}
        
        Hãy truy cập website để đọc bài viết mới.
        """
        
        for email in subscriber_emails:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            logger.info(f"Blog notification sent to {email}")
            
        return True
        
    except Exception as exc:
        logger.error(f"Failed to send blog notification: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=120,  # 2 phút, 4 phút, 8 phút...
    retry_kwargs={"max_retries": 3},
    name="resend_verification_email"
)
def resend_verification_email_task(self, user_id, user_email):
    """
    Task gửi lại email xác thực cho user.
    
    Args:
        user_id: ID của user
        user_email: Email của user
    
    Returns:
        bool: True nếu gửi thành công
    """
    try:
        User = get_user_model()
        user = User.objects.get(id=user_id, email=user_email)
        
        # Kiểm tra xem user đã được kích hoạt chưa
        if user.is_active:
            logger.info(f"User {user_email} is already active, skipping resend")
            return True
        
        # Tạo token xác thực mới
        token_data = {
            "user_id": user.id,
            "email": user.email
        }
        token = signing.dumps(token_data, salt="email-verify")
        
        # Tạo URL xác thực (cần domain từ settings)
        verify_url = f"{settings.SITE_URL}/api/verify-email/?token={token}"
        
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
        
        # Gửi email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Verification email resent successfully to {user_email}")
        return True
        
    except User.DoesNotExist:
        logger.error(f"User {user_email} not found for resend")
        return False
    except Exception as exc:
        logger.error(f"Failed to resend verification email to {user_email}: {str(exc)}")
        raise self.retry(exc=exc)
