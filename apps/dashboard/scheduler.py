import time
from django.utils import timezone
from django.conf import settings
import os

def start_scheduler():
    """این تابع در پس‌زمینه اجرا می‌شود و هر ۶۰ ثانیه دیتابیس را چک می‌کند"""
    print("\n⏰ سرویس زمان‌بندی (Scheduler) فعال شد. (هر ۶۰ ثانیه چک می‌کند)")
    
    while True:
        try:
            # مدل‌ها را اینجا ایمپورت می‌کنیم تا خطای لود شدن ندهد
            from apps.content_engine.models import VideoProject
            
            # فقط تلاش برای ایمپورت ماژول‌های آپلودر (چون شاید نصب نباشند)
            TelegramUploader = None
            YouTubeUploader = None
            try: from apps.telegram_manager.telegram_service import TelegramUploader
            except: pass
            try: from apps.youtube_manager.youtube_service import YouTubeUploader
            except: pass

            now = timezone.now()
            
            # پروژه‌هایی که: ۱.ویدیو دارند ۲.زمانشان رسیده ۳.هنوز آپلود نشده‌اند
            pending_projects = VideoProject.objects.filter(
                status='video_ready',
                scheduled_upload__lte=now,
                scheduled_upload__isnull=False
            )

            if pending_projects.exists():
                print(f"\n🚀 یافتن {pending_projects.count()} پروژه زمان‌بندی شده...")

            for project in pending_projects:
                print(f"   ⏳ ارسال خودکار: {project.topic} ({project.platform})")
                
                # --- ارسال تلگرام ---
                if project.platform == 'telegram' and TelegramUploader:
                    uploader = TelegramUploader()
                    success = False
                    
                    # حالت فروشگاهی
                    if project.project_type == 'product_post':
                        photo = None
                        if project.images.exists(): photo = project.images.first().image.path
                        elif project.thumbnail_path: photo = os.path.join(settings.MEDIA_ROOT, project.thumbnail_path)
                        
                        if photo:
                            brand = project.brand_name or "-"
                            price = project.get_final_price() if hasattr(project, 'get_final_price') else 0
                            caption = f"🔥 {project.topic}\n\n{project.script_text}\n\n🏷 {brand}\n💰 {price:,} تومان"
                            if hasattr(uploader, 'send_photo'): success = uploader.send_photo(photo, caption)
                            else: success = uploader.send_video(photo, caption)

                    # حالت ویدیویی
                    elif project.video_path:
                        path = os.path.join(settings.MEDIA_ROOT, project.video_path)
                        cap = f"{project.generated_title}\n\n{project.generated_description}"
                        success = uploader.send_video(path, cap)

                    if success:
                        project.status = 'uploaded'
                        project.save()
                        print(f"   ✅ با موفقیت به تلگرام ارسال شد.")

                # --- ارسال یوتیوب (اگر نیاز بود خودکار شود) ---
                elif project.platform == 'youtube' and YouTubeUploader:
                    # برای یوتیوب معمولاً دستی بهتر است، اما اگر اینجا رسید یعنی کاربر خواسته
                    uploader = YouTubeUploader()
                    path = os.path.join(settings.MEDIA_ROOT, project.video_path)
                    if os.path.exists(path):
                         vid_id = uploader.upload_video(path, project.generated_title, project.generated_description)
                         if vid_id:
                             project.status = 'uploaded'
                             project.save()
                             print(f"   ✅ با موفقیت به یوتیوب ارسال شد.")

        except Exception as e:
            print(f"⚠️ خطای اسکجولر: {e}")

        # ۶۰ ثانیه خواب
        time.sleep(30)