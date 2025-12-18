import edge_tts
import asyncio
import os
from django.conf import settings
import uuid
from gtts import gTTS  # لاستیک زاپاس

class AudioGenerator:
    def generate_voice(self, text, project_id):
        # ساخت نام فایل
        filename = f"voice_{project_id}_{uuid.uuid4().hex[:8]}.mp3"
        save_path = os.path.join(settings.MEDIA_ROOT, 'voices', filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # مسیر نسبی برای دیتابیس
        relative_path = f"voices/{filename}"

        print(f"--- تلاش برای تولید صدا (مایکروسافت)... ---")
        
        # 1. تلاش اول: مایکروسافت Edge (کیفیت بالا)
        try:
            asyncio.run(self._save_edge_tts(text, save_path))
            print("✅ صدا با کیفیت عالی (Microsoft) تولید شد.")
            return relative_path
            
        except Exception as e:
            print(f"⚠️ مایکروسافت اجازه نداد (خطا: {e})")
            print("--- سوییچ به حالت اضطراری (Google)... ---")
            
            # 2. تلاش دوم: گوگل (کیفیت معمولی ولی مطمئن)
            try:
                self._save_google_tts(text, save_path)
                print("✅ صدا با کیفیت معمولی (Google) تولید شد.")
                return relative_path
            except Exception as e2:
                print(f"❌ گوگل هم شکست خورد: {e2}")
                return None

    async def _save_edge_tts(self, text, output_file):
        """تولید صدا با مایکروسافت
        صداهای انتخاب شده:
        1. انگلیسی: GuyNeural (مرد)
        2. فارسی: FaridNeural (مرد)
        """
        # پیش‌فرض: صدای مرد انگلیسی
        voice = 'en-US-GuyNeural' 
        
        # تشخیص زبان فارسی (اگر حروف الفبای فارسی/عربی دید)
        if any("\u0600" <= char <= "\u06FF" for char in text):
             # صدای مرد فارسی
             voice = 'fa-IR-FaridNeural'

        # ارسال درخواست به مایکروسافت
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)

    def _save_google_tts(self, text, output_file):
        """تولید صدا با گوگل (نسخه پشتیبان)"""
        # تشخیص زبان برای گوگل
        lang = 'en'
        if any("\u0600" <= char <= "\u06FF" for char in text):
            lang = 'fa'
            
        # نکته: گوگل انتخاب جنسیت ندارد و پیش‌فرض خودش را استفاده می‌کند
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(output_file)