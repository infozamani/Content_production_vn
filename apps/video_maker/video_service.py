from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips, CompositeAudioClip, CompositeVideoClip
import PIL.Image
from PIL import Image, ImageDraw, ImageFont
import os
import json
import shutil
from django.conf import settings
import uuid
import arabic_reshaper
from bidi.algorithm import get_display

# --- 🚑 بخش اورژانس: رفع خطای ANTIALIAS (سازگاری با نسخه جدید پایتون) ---
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
    PIL.Image.Resampling = PIL.Image
# -------------------------------------------------------------------

from apps.content_engine.audio_service import AudioGenerator
from apps.video_maker.graph_service import GraphGenerator
from apps.content_engine.ai_service import ContentGenerator

# --- ایمپورت سرویس جدید تصویرساز (DALL-E) ---
try:
    from apps.video_maker.image_gen_service import ImageGenerator
except ImportError:
    ImageGenerator = None
    print("⚠️ هشدار: فایل image_gen_service.py پیدا نشد.")

class VideoGenerator:
    def __init__(self):
        self.audio_gen = AudioGenerator()
        self.graph_gen = GraphGenerator()
        self.text_gen = ContentGenerator() # برای روش رایگان (Pollinations)
        
        # راه‌اندازی سرویس DALL-E (اگر موجود باشد)
        if ImageGenerator:
            self.img_gen = ImageGenerator()
        else:
            self.img_gen = None

    # متد اصلی ساخت ویدیو از متن (JSON)
    def create_video_from_json(self, json_script, topic, project_id):
        print(f"--- 🎬 شروع ساخت ویدیو برای پروژه {project_id} ---")
        return self._process_video_generation(json_script, project_id, mode='text', topic=topic)

    # متد ساخت ویدیو از عکس‌های آپلودی (Vision)
    def create_video_from_uploaded_images(self, json_script, image_paths, project_id):
        print(f"--- 📸 شروع ساخت ویدیو (حالت ویژن) برای پروژه {project_id} ---")
        return self._process_video_generation(json_script, project_id, mode='image', image_paths=image_paths)

    # موتور اصلی پردازش
    def _process_video_generation(self, json_script, project_id, mode='text', topic=None, image_paths=None):
        # ایجاد پوشه موقت برای پروژه
        project_dir_name = f"project_{project_id}_{uuid.uuid4().hex[:4]}"
        project_path = os.path.join(settings.MEDIA_ROOT, 'projects', project_dir_name)
        os.makedirs(project_path, exist_ok=True)

        try:
            # === ۱. استانداردسازی JSON ===
            try:
                raw_data = json.loads(json_script)
            except:
                print("❌ خطا: فرمت JSON نامعتبر است.")
                return None

            segments = []
            # هندل کردن ساختارهای مختلف JSON (لیست یا دیکشنری)
            if isinstance(raw_data, dict):
                if 'script_segments' in raw_data:
                    segments = raw_data['script_segments']
                elif 'script' in raw_data:
                    segments = raw_data['script']
                else:
                    segments = [raw_data] 
            elif isinstance(raw_data, list):
                segments = raw_data
            
            if not segments:
                print("❌ خطا: هیچ سگمنتی برای ساخت ویدیو پیدا نشد!")
                return None
            # ==============================

            clips = []
            
            for index, segment in enumerate(segments):
                narration = segment.get('narration', '')
                if not narration: continue

                print(f"   ... در حال پردازش صحنه {index + 1}")

                # === ۲. تولید صدا ===
                audio_rel_path = self.audio_gen.generate_voice(narration, f"{project_id}_{index}")
                if not audio_rel_path: 
                    print("      ⚠️ خطا در تولید صدا، رد کردن این صحنه.")
                    continue

                original_audio_path = os.path.join(settings.MEDIA_ROOT, audio_rel_path)
                final_audio_path = os.path.join(project_path, f"audio_{index}.mp3")
                
                # کپی فایل صدا به پوشه پروژه
                if os.path.exists(original_audio_path):
                    shutil.copy(original_audio_path, final_audio_path)
                else:
                    continue

                # === ۳. تولید تصویر ===
                image_path = None
                
                # الف) حالت متنی (ساخت عکس با هوش مصنوعی)
                if mode == 'text':
                    visual_prompt = segment.get('visual', '')
                    
                    # اگر دستور IMG: دارد
                    if "IMG:" in str(visual_prompt):
                        clean_prompt = str(visual_prompt).replace("IMG:", "").strip()
                        
                        # اولویت ۱: استفاده از DALL-E (اگر فعال باشد)
                        if self.img_gen:
                            image_path = self.img_gen.generate_image(clean_prompt, project_id)
                        
                        # اولویت ۲: استفاده از Pollinations (اگر DALL-E نبود یا خطا داد)
                        if not image_path:
                             print("      ⚠️ سوییچ به حالت رایگان (Pollinations)...")
                             gen_img_path = os.path.join(project_path, f"ai_gen_{index}.jpg")
                             # استفاده از متد کلاس ContentGenerator که قبلاً داشتیم
                             if self.text_gen.generate_image_from_prompt(clean_prompt, gen_img_path):
                                 image_path = gen_img_path
                    
                    # اگر عکس ساخته نشد یا دستور عکس نداشت، اسلاید متنی بساز
                    if not image_path:
                        content = segment.get('content', segment.get('visual', topic))
                        clean_content = str(content).replace("IMG:", "")
                        image_path = self._create_title_image(clean_content, project_path, index)
                
                # ب) حالت تصویری (استفاده از عکس‌های آپلود شده)
                elif mode == 'image':
                    if image_paths:
                        safe_idx = index % len(image_paths)
                        source_img = image_paths[safe_idx]
                        dest_img = os.path.join(project_path, f"slide_{index}.jpg")
                        try:
                            shutil.copy(source_img, dest_img)
                            image_path = dest_img
                        except: pass

                # اگر هیچ عکسی جور نشد، یک صفحه سیاه با متن بساز
                if not image_path or not os.path.exists(image_path):
                    image_path = self._create_title_image(narration[:50], project_path, index)

                # === ۴. مونتاژ کلیپ (صدا + تصویر) ===
                try:
                    safe_image = image_path.replace('\\', '/')
                    safe_audio = final_audio_path.replace('\\', '/')
                    
                    audio_clip = AudioFileClip(safe_audio)
                    # افزودن کمی سکوت به انتهای هر جمله برای طبیعی‌تر شدن
                    duration = audio_clip.duration + 0.2
                    
                    # ساخت کلیپ تصویری
                    img_clip = ImageClip(safe_image).resize((1920, 1080)).set_duration(duration).set_fps(24)
                    video_clip = img_clip.set_audio(audio_clip)
                    
                    clips.append(video_clip)
                except Exception as e:
                    print(f"      ❌ خطا در مونتاژ کلیپ {index}: {e}")

            # === ۵. رندر نهایی ===
            if clips:
                print("   ... در حال رندر و چسباندن کلیپ‌ها (لطفاً صبر کنید)")
                final_video = concatenate_videoclips(clips, method="compose")
                
                output_filename = f"final_{project_id}.mp4"
                output_full_path = os.path.join(project_path, output_filename)
                
                # رندر با تنظیمات سریع
                final_video.write_videofile(
                    output_full_path, 
                    codec="libx264", 
                    audio_codec="aac", 
                    fps=24,
                    preset='ultrafast',
                    threads=4,
                    logger=None # لاگ‌های اضافی moviepy را حذف می‌کند تا ترمینال شلوغ نشود
                )
                
                # بستن منابع
                final_video.close()
                for c in clips: c.close()
                
                # بازگرداندن مسیر نسبی (views.py این را می‌گیرد و جابجا می‌کند)
                return f"projects/{project_dir_name}/{output_filename}"
            
            return None

        except Exception as e:
            print(f"❌ خطای کلی در VideoGenerator: {e}")
            import traceback
            traceback.print_exc()
            return None

    # تابع کمکی برای ساخت اسلاید متنی (وقتی عکس نداریم)
    def _create_title_image(self, text_content, project_path, index):
        width, height = 1920, 1080
        img = Image.new('RGB', (width, height), color='#1a1a2e')
        draw = ImageDraw.Draw(img)
        
        # فارسی‌ساز
        try:
            reshaped = arabic_reshaper.reshape(text_content)
            bidi_text = get_display(reshaped)
        except:
            bidi_text = text_content

        # فونت
        try:
            font_paths = ["arial.ttf", "segoeui.ttf", "tahoma.ttf"]
            font = None
            for fp in font_paths:
                try:
                    font = ImageFont.truetype(fp, 70)
                    break
                except: continue
            if not font: font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()

        # وسط‌چین
        bbox = draw.textbbox((0, 0), bidi_text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        draw.text(((width - text_w) / 2, (height - text_h) / 2), bidi_text, font=font, fill='white')
        
        save_path = os.path.join(project_path, f"text_{index}.jpg")
        img.save(save_path)
        return save_path