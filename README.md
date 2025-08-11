# Blog Backend API

## 📋 Mô tả dự án

Blog Backend API là một ứng dụng backend được xây dựng bằng Django REST Framework, cung cấp API cho hệ thống blog với các tính năng quản lý người dùng, bài viết và xác thực JWT.

## 🛠️ Công nghệ sử dụng

### Backend Framework
- **Django 5.2.4** - Web framework chính
- **Django REST Framework 3.16.0** - Framework để xây dựng REST API
- **ASGI 3.9.1** - Asynchronous Server Gateway Interface

### Database
- **SQLite3** - Cơ sở dữ liệu (development)
- **Django ORM** - Object-Relational Mapping

### Authentication & Security
- **Django REST Framework Simple JWT 5.5.1** - JSON Web Token authentication
- **PyJWT 2.10.1** - Python library cho JWT
- **Django CORS Headers 4.7.0** - Cross-Origin Resource Sharing

### File Handling
- **Pillow 11.3.0** - Python Imaging Library cho xử lý hình ảnh
- **Django Media Files** - Quản lý upload và serve media files

### Deployment & Production
- **Gunicorn 23.0.0** - WSGI HTTP Server cho production
- **Build Script** - Automated deployment script

### Development Tools
- **SQLParse 0.5.3** - SQL parsing và formatting
- **Packaging 25.0** - Core utilities cho Python packages
- **TZData 2025.2** - Timezone database

## 🚀 Tính năng chính

### 👤 Quản lý người dùng
- Đăng ký tài khoản mới
- Thông tin profile chi tiết (bio, job title, social links)
- Upload và quản lý ảnh đại diện
- Tích hợp social media links (Facebook, YouTube, Instagram, Twitter, LinkedIn)

### 📝 Quản lý bài viết
- Tạo, chỉnh sửa, xóa bài viết
- Hệ thống draft/publish
- Phân loại bài viết theo categories
- Upload ảnh đại diện cho bài viết
- Slug tự động tạo từ title
- Pagination cho danh sách bài viết

### 🔐 Xác thực & Bảo mật
- JWT Authentication
- CORS configuration cho frontend
- Permission-based access control
- Secure file uploads

### 📊 Categories
- Frontend
- Backend
- Fullstack
- Design
- Blockchain
- DevOps
- AI
- Other

## 🏗️ Cấu trúc dự án

```
BE_BLOG/
├── app/                    # Main application
│   ├── models.py          # Database models
│   ├── views.py           # API views
│   ├── serializers.py     # DRF serializers
│   ├── urls.py            # URL routing
│   └── migrations/        # Database migrations
├── BE_BLOG/               # Project settings
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI configuration
├── media/                 # Uploaded files
│   ├── blog_img/          # Blog images
│   └── profile_img/       # Profile pictures
├── requirements.txt       # Python dependencies
├── build.sh              # Deployment script
└── manage.py             # Django management script
```

## 📦 Cài đặt

### Yêu cầu hệ thống
- Python 3.8+
- pip
- Virtual environment (khuyến nghị)

### Bước 1: Clone repository
```bash
git clone <repository-url>
cd BE_BLOG
```

### Bước 2: Tạo virtual environment
```bash
python -m venv env
# Windows
env\Scripts\activate
# Linux/Mac
source env/bin/activate
```

### Bước 3: Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### Bước 4: Cấu hình database
```bash
python manage.py makemigrations
python manage.py migrate
```

### Bước 5: Tạo superuser (tùy chọn)
```bash
python manage.py createsuperuser
```

### Bước 6: Chạy development server
```bash
python manage.py runserver
```

## 🔧 Cấu hình

### Environment Variables
Tạo file `.env` trong thư mục gốc:
```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,https://your-frontend-domain.com
```

### CORS Configuration
Cấu hình CORS trong `settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://your-frontend-domain.com",
]
```

## 📡 API Endpoints

### Authentication
- `POST /api/register/` - Đăng ký người dùng mới
- `POST /api/token/` - Lấy JWT token
- `POST /api/token/refresh/` - Refresh JWT token

### Users
- `GET /api/userinfo/{username}/` - Lấy thông tin người dùng
- `GET /api/username/` - Lấy username hiện tại (authenticated)
- `PUT /api/update-profile/` - Cập nhật profile (authenticated)

### Blogs
- `GET /api/blogs/` - Danh sách bài viết (paginated)
- `GET /api/blogs/{slug}/` - Chi tiết bài viết theo slug
- `POST /api/create-blog/` - Tạo bài viết mới (authenticated)
- `PUT /api/update-blog/{id}/` - Cập nhật bài viết (authenticated)
- `POST /api/delete-blog/{id}/` - Xóa bài viết (authenticated)

## 🚀 Deployment

### Sử dụng build script
```bash
chmod +x build.sh
./build.sh
```

### Manual deployment
```bash
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
gunicorn BE_BLOG.wsgi:application
```

## 📁 Media Files

Dự án hỗ trợ upload và quản lý:
- **Blog Images**: Lưu trong `media/blog_img/`
- **Profile Pictures**: Lưu trong `media/profile_img/`

## 🔒 Bảo mật

- JWT Authentication cho API endpoints
- CORS configuration cho cross-origin requests
- File upload validation
- Permission-based access control
- Secure password validation

## 🤝 Đóng góp

1. Fork dự án
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request


## 📞 Liên hệ
- **Project Link**: [https://github.com/cnnuyndev/Blogs_BE]

## 🙏 Acknowledgments

- Django Documentation
- Django REST Framework Documentation
- JWT Documentation
- Pillow Documentation 
