import google.generativeai as genai
import os
import json
import re
from PIL import Image
import requests
import urllib.parse
import uuid

class ContentGenerator:
    def __init__(self):
        # دریافت کلید
        raw_key = os.getenv("GOOGLE_API_KEY")
        api_key = raw_key.strip() if raw_key else None
        
        if not api_key:
            print("--- ⚠️ هشدار: کلید گوگل پیدا نشد ---")
            self.model = None
        else:
            try:
                genai.configure(api_key=api_key)
                # استفاده از مدل 2.5 فلش که روی سیستم شما جواب داد
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                print("✅ مدل Gemini 2.5 Flash متصل شد.")
            except Exception as e:
                print(f"❌ خطا در اتصال به گوگل: {e}")
                self.model = None

    def _get_role_description(self, style):
        if style == 'math': return "ACT AS A MATH TEACHER."
        elif style == 'story': return "ACT AS A STORYTELLER."
        elif style == 'sales': return "ACT AS A PROFESSIONAL MARKETER."
        return "ACT AS A HELPFUL ASSISTANT."

    def _extract_json(self, text):
        if not text: return None
        text = text.replace('```json', '').replace('```', '').strip()
        match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
        if match:
            return match.group()
        return None

    # --- متد ۱: تولید سناریو از متن (وقتی عکس آپلود نکردید) ---
    def generate_script(self, topic, duration='short', style='general'):
        print(f"--- 🧠 (Text Mode) درخواست سناریو برای: {topic} ---")
        if not self.model: return None

        role = self._get_role_description(style)
        
        # اگر سبک فروشگاهی است (برای تلگرام)
        if style == 'sales':
            prompt = (
                f"{role} Write a persuasive caption for product: '{topic}'. "
                "Output JSON with key 'narration'."
            )
        else:
            # اگر ویدیوی معمولی است (یوتیوب/اینستا)
            # اینجا به هوش مصنوعی می‌گوییم توصیف عکس (IMG) هم بسازد
            prompt = (
                f"{role} Write a video script about '{topic}'. "
                "OUTPUT FORMAT: JSON Array only. "
                "Structure: [{'narration': '...', 'visual': 'IMG: detailed description for image generation...'}, ...]"
                "Make sure 'visual' starts with 'IMG:' so we can generate images."
            )

        try:
            response = self.model.generate_content(prompt)
            return self._extract_json(response.text)
        except Exception as e:
            print(f"--- AI Error: {e} ---")
            return None

    # --- متد ۲: تولید سناریو از عکس (Vision Mode) [این بخش قبلاً خالی بود] ---
    def generate_script_from_images(self, topic, image_paths, style='general', duration='short'):
        print(f"--- 👁️ (Vision Mode) تفسیر {len(image_paths)} عکس ---")
        if not self.model: return None

        role = self._get_role_description(style)
        
        try:
            # بارگذاری تصاویر
            image_objects = []
            for path in image_paths:
                if os.path.exists(path):
                    image_objects.append(Image.open(path))
            
            if not image_objects:
                print("--- عکسی پیدا نشد ---")
                return None

            prompt_text = (
                f"{role} I have uploaded {len(image_paths)} images about '{topic}'. "
                "Create a video narration script that matches these images in order. "
                "OUTPUT: Valid JSON Array. "
                "Structure: [{'narration': 'Explanation for this slide...'}, ...]"
            )

            # ارسال همزمان متن و عکس به جمنای
            input_content = [prompt_text] + image_objects
            
            response = self.model.generate_content(input_content)
            extracted = self._extract_json(response.text)
            
            if extracted:
                print("✅ سناریو از روی عکس‌ها ساخته شد.")
            else:
                print("⚠️ خروجی AI نامعتبر بود.")
                
            return extracted

        except Exception as e:
            print(f"--- AI Vision Error: {e} ---")
            return None

    # --- متد ۳: سئو ---
    def generate_seo(self, topic, script):
        if not self.model: return None
        try:
            preview = str(script)[:1000]
            prompt = f"Generate JSON SEO (title, description, tags) for video about '{topic}'."
            res = self.model.generate_content(prompt)
            return self._extract_json(res.text)
        except: return None

    # --- متد ۴: ساخت عکس (Pollinations) ---
    def generate_image_from_prompt(self, prompt, save_path):
        print(f"--- 🎨 ساخت عکس (رایگان): {prompt[:30]}... ---")
        try:
            encoded = urllib.parse.quote(prompt)
            seed = uuid.uuid4().int
            url = f"https://image.pollinations.ai/prompt/{encoded}?width=1920&height=1080&nologo=true&seed={seed}&model=flux"
            res = requests.get(url, timeout=40)
            if res.status_code == 200:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, 'wb') as f: f.write(res.content)
                return True
            return False
        except: return False