from django.contrib import admin
from django.urls import path, include
# --- اضافه کردن این دو خط برای فایل‌های مدیا ---
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
    # ... اگر مسیرهای دیگر دارید ...
]

# --- جادوی اصلی: فعال‌سازی دانلود فایل‌ها ---
# این دستور می‌گوید: اگر در حالت دیباگ هستیم، فایل‌های مدیا را سرویس بده
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)