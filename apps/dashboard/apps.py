from django.apps import AppConfig
import os
import threading

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.dashboard'

    def ready(self):
        # اجرای ربات فقط در پروسه اصلی سرور (جلوگیری از اجرای دوبار)
        if os.environ.get('RUN_MAIN') == 'true':
            try:
                # نام تابع باید دقیقاً با فایل scheduler.py یکی باشد
                from .scheduler import start_scheduler
                
                # اجرا در ترد جداگانه
                t = threading.Thread(target=start_scheduler, daemon=True)
                t.start()
            except ImportError as e:
                print(f"❌ خطا در اجرای اسکجولر: {e}")