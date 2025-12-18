from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
import os
import json
import threading
import shutil 

from apps.content_engine.models import VideoProject, ProjectImage
from .forms import VideoProjectForm
from apps.content_engine.ai_service import ContentGenerator
from apps.video_maker.video_service import VideoGenerator
from apps.youtube_manager.youtube_service import YouTubeUploader

try:
    from apps.telegram_manager.telegram_service import TelegramUploader
except ImportError:
    TelegramUploader = None

# =========================================================
#  بخش ۱: توابع کمکی (Helper Functions)
# =========================================================

def _auto_upload_telegram(project):
    """تابع کمکی برای ارسال به تلگرام"""
    if not TelegramUploader: 
        print("⚠️ ماژول تلگرام نصب نیست.")
        return False
        
    print(f"🚀 شروع ارسال به تلگرام ({project.project_type})...")
    uploader = TelegramUploader()
    
    try:
        # حالت ۱: پست فروشگاهی (عکس + کپشن)
        if project.project_type == 'product_post':
            photo = None
            if project.images.exists(): photo = project.images.first().image.path
            elif project.thumbnail_path: photo = os.path.join(settings.MEDIA_ROOT, project.thumbnail_path)
            
            if photo and os.path.exists(photo):
                final_price = project.get_final_price() if hasattr(project, 'get_final_price') else 0
                brand = project.brand_name or "-"
                caption = (
                    f"🔥 <b>{project.topic}</b>\n\n{project.script_text}\n\n"
                    f"🏷 برند: {brand}\n💰 قیمت: {final_price:,} تومان\n🆔 @Channel"
                )
                if hasattr(uploader, 'send_photo'): uploader.send_photo(photo, caption)
                else: uploader.send_video(photo, caption)
                
                project.status = 'uploaded'
                project.save()
                print("✅ تلگرام: پست فروشگاهی ارسال شد.")
                return True
        
        # حالت ۲: ویدیو
        elif project.video_path:
            full_path = os.path.join(settings.MEDIA_ROOT, project.video_path)
            if os.path.exists(full_path):
                caption = f"{project.generated_title}\n\n{project.generated_description}"
                if uploader.send_video(full_path, caption):
                    project.status = 'uploaded'
                    project.save()
                    print("✅ تلگرام: ویدیو ارسال شد.")
                    return True
    except Exception as e:
        print(f"❌ خطا در ارسال تلگرام: {e}")
    
    return False

def _auto_upload_youtube(project):
    """تابع کمکی برای آپلود در یوتیوب"""
    print("🚀 شروع آپلود در یوتیوب...")
    try:
        uploader = YouTubeUploader()
        full_path = os.path.join(settings.MEDIA_ROOT, project.video_path)
        
        if not os.path.exists(full_path):
            print("❌ فایل ویدیو یافت نشد.")
            return False

        title = project.generated_title or project.topic
        desc = project.generated_description or project.topic
        if project.generated_tags: desc += f"\n\nTags: {project.generated_tags}"
        
        vid_id = uploader.upload_video(full_path, title, desc)
        if vid_id:
            project.status = 'uploaded'
            project.save()
            print(f"✅ یوتیوب آپلود شد: {vid_id}")
            return True
    except Exception as e:
        print(f"⚠️ خطا در آپلود یوتیوب: {e}")
    return False


# =========================================================
#  بخش ۲: ویوها (Views)
# =========================================================

def home(request):
    current_platform = request.GET.get('platform', 'youtube')

    if request.method == 'POST':
        form = VideoProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.platform = current_platform
            
            images = request.FILES.getlist('images')
            
            # تشخیص هوشمند نوع پروژه
            if not project.project_type:
                if current_platform == 'telegram' and images:
                     project.project_type = 'product_post'
                elif images:
                    project.project_type = 'image_based'
                else:
                    project.project_type = 'topic_based'
            
            project.save()

            if images:
                for i, f in enumerate(images):
                    ProjectImage.objects.create(project=project, image=f, order=i)

            messages.success(request, f"✅ پروژه ایجاد شد.")
            return redirect(f'/?platform={current_platform}')
        else:
            messages.error(request, f"خطا در فرم: {form.errors.as_text()}")
    else:
        form = VideoProjectForm()

    projects = VideoProject.objects.filter(platform=current_platform).order_by('-created_at')
    return render(request, 'dashboard/home.html', {'projects': projects, 'form': form, 'current_platform': current_platform})

def delete_project(request, project_id):
    project = get_object_or_404(VideoProject, id=project_id)
    p = project.platform
    project.delete()
    messages.success(request, "🗑️ حذف شد.")
    return redirect(f'/?platform={p}')

def edit_project(request, project_id):
    project = get_object_or_404(VideoProject, id=project_id)
    if request.method == 'POST':
        form = VideoProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ ذخیره شد.")
            return redirect(f'/?platform={project.platform}')
    else:
        form = VideoProjectForm(instance=project)
    return render(request, 'dashboard/edit_project.html', {'form': form, 'project': project})

# ---------------------------------------------------------
#  مغز متفکر: شروع پردازش (با کنترل زمان‌بندی و دستی بودن یوتیوب)
# ---------------------------------------------------------
def start_generation(request, project_id):
    project = get_object_or_404(VideoProject, id=project_id)
    project.status = 'processing'
    project.save()

    def run_process():
        print(f"🚀 شروع پردازش: {project.topic} | پلتفرم: {project.platform}")
        ai = ContentGenerator()
        video_gen = VideoGenerator()
        
        target_dir = os.path.join(settings.MEDIA_ROOT, project.platform)
        os.makedirs(target_dir, exist_ok=True)

        try:
            # === مسیر ۱: پست فروشگاهی تلگرام (بدون ویدیو) ===
            if project.platform == 'telegram' and project.project_type == 'product_post':
                if not project.script_text:
                    print("   🛍️ تولید کپشن محصول...")
                    caption = ai.generate_script(project.topic, style='sales')
                    if caption and "narration" in caption:
                        try:
                            data = json.loads(caption)
                            if isinstance(data, dict): caption = data.get('narration', '')
                            elif isinstance(data, list): caption = data[0].get('narration', '')
                        except: pass
                    project.script_text = caption if caption else project.topic
                
                project.status = 'video_ready'
                project.save()
                
                # --- منطق ارسال تلگرام ---
                # فقط اگر زمان‌بندی "نداشته" باشد، الان می‌فرستیم
                if not project.scheduled_upload:
                    _auto_upload_telegram(project)
                else:
                    print(f"⏳ پروژه برای {project.scheduled_upload} زمان‌بندی شده است. ارسال متوقف شد.")
                return

            # === مسیر ۲: ویدیو (یوتیوب / اینستاگرام / تلگرام ویدیویی) ===
            print("   🎬 شروع پروسه ساخت ویدیو...")
            has_images = project.images.exists()
            
            # الف) تولید سناریو
            if not project.script_text:
                if has_images:
                    paths = [img.image.path for img in project.images.all()]
                    res = ai.generate_script_from_images(project.topic, paths, style=project.narrator_style)
                else:
                    res = ai.generate_script(project.topic, style=project.narrator_style)
                
                if res:
                    project.script_text = res
                    project.status = 'script_ready'
                    project.save()
                    # سئو
                    seo = ai.generate_seo(project.topic, res)
                    if seo:
                        try:
                            d = json.loads(seo)
                            project.generated_title = d.get('title')
                            project.generated_description = d.get('description')
                            project.generated_tags = d.get('tags')
                            project.save()
                        except: pass
                else:
                    print("❌ هوش مصنوعی خروجی نداد.")
                    project.status = 'failed'
                    project.save()
                    return

            # ب) رندر ویدیو
            if project.script_text:
                print("   🎥 رندر ویدیو...")
                vid_path = None
                
                if has_images:
                    paths = [img.image.path for img in project.images.all()]
                    vid_path = video_gen.create_video_from_uploaded_images(project.script_text, paths, project.id)
                else:
                    vid_path = video_gen.create_video_from_json(project.script_text, project.topic, project.id)
                
                if vid_path:
                    # انتقال فایل
                    full_p = os.path.join(settings.MEDIA_ROOT, vid_path)
                    new_name = os.path.basename(vid_path)
                    new_path = os.path.join(target_dir, new_name)
                    try: shutil.move(full_p, new_path)
                    except: new_path = full_p
                    
                    project.video_path = f"{project.platform}/{new_name}"
                    project.status = 'video_ready'
                    project.save()
                    print(f"   ✅ ویدیو آماده شد: {new_name}")
                    
                    # --- منطق ارسال نهایی ---
                    
                    # ۱. تلگرام: اگر زمان‌بندی ندارد، بفرست
                    if project.platform == 'telegram':
                        if not project.scheduled_upload:
                            _auto_upload_telegram(project)
                        else:
                            print(f"⏳ تلگرام زمان‌بندی شده است. ارسال متوقف شد.")

                    # ۲. یوتیوب: همیشه دستی (طبق دستور شما)
                    elif project.platform == 'youtube':
                        print("🏁 ویدیو یوتیوب آماده است. (منتظر تایید دستی شما)")
                        # اینجا _auto_upload_youtube را صدا نمی‌زنیم تا خودتان دکمه را بزنید

                else:
                    print("❌ ویدیو ساخته نشد.")
                    project.status = 'failed'
                    project.save()

        except Exception as e:
            print(f"❌ خطای پردازش: {e}")
            project.status = 'failed'
            project.save()

    thread = threading.Thread(target=run_process)
    thread.start()
    messages.info(request, "⏳ پردازش شروع شد...")
    return redirect(f'/?platform={project.platform}')


# ---------------------------------------------------------
#  آپلود دستی (دکمه‌های داشبورد)
# ---------------------------------------------------------
def upload_telegram(request, project_id):
    project = get_object_or_404(VideoProject, id=project_id)
    success = _auto_upload_telegram(project)
    if success: messages.success(request, "✅ ارسال شد.")
    else: messages.error(request, "❌ خطا در ارسال.")
    return redirect(f'/?platform={project.platform}')

def upload_youtube(request, project_id):
    project = get_object_or_404(VideoProject, id=project_id)
    # این دکمه حالا فقط وقتی زده می‌شود که شما ویدیو را دیده و تایید کرده باشید
    success = _auto_upload_youtube(project)
    if success: messages.success(request, "✅ ارسال شد.")
    else: messages.error(request, "❌ خطا در ارسال.")
    return redirect(f'/?platform={project.platform}')