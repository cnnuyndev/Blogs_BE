from django.contrib import admin
from .models import CustomUser, Blog
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Blog)
