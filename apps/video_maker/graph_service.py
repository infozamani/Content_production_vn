import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
from django.conf import settings
import uuid
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

class GraphGenerator:
    def __init__(self):
        plt.style.use('dark_background')

    def create_plot(self, formula, project_id):
        # (کد قبلی رسم نمودار - بدون تغییر)
        try:
            x = np.linspace(-10, 10, 500)
            allowed_names = {"x": x, "np": np, "sin": np.sin, "cos": np.cos, "tan": np.tan, "abs": np.abs, "sqrt": np.sqrt, "log": np.log10, "exp": np.exp}
            y = eval(formula, {"__builtins__": None}, allowed_names)
            
            fig, ax = plt.subplots(figsize=(12, 7))
            fig.patch.set_facecolor('#1e1e1e')
            ax.set_facecolor('#1e1e1e')
            
            ax.plot(x, y, color='#4cc9f0', linewidth=6, alpha=0.3)
            ax.plot(x, y, color='#f72585', linewidth=3)
            ax.fill_between(x, y, alpha=0.1, color='#f72585')
            ax.axhline(0, color='white', linewidth=1)
            ax.axvline(0, color='white', linewidth=1)
            ax.grid(True, linestyle=':', alpha=0.4)
            
            # حذف حاشیه‌ها برای استفاده در کاور
            ax.axis('off')
            
            output_path = os.path.join(settings.MEDIA_ROOT, 'raw_images', f"plot_{uuid.uuid4().hex}.png")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            plt.savefig(output_path, facecolor=fig.get_facecolor(), bbox_inches='tight', pad_inches=0)
            plt.close()
            return output_path
        except:
            return None

    def create_formula_slide(self, text, project_id):
        # (کد قبلی اسلاید فرمول - بدون تغییر)
        # اگر کدش را دارید دست نزنید، اگر ندارید از چت‌های قبل بردارید
        return None 

    # --- تابع جدید برای ساخت کاور یوتیوب ---
    def create_thumbnail(self, topic, project_id):
        print(f"--- در حال ساخت کاور جذاب برای: {topic} ---")
        try:
            # 1. ابعاد استاندارد یوتیوب
            width, height = 1280, 720
            
            # 2. ساخت پس‌زمینه (رنگ سرمه‌ای تیره جذاب)
            img = Image.new('RGB', (width, height), color='#0f2027')
            draw = ImageDraw.Draw(img)

            # 3. افزودن یک گرافیک تزیینی (یک نمودار محو در پس‌زمینه)
            # یک نمودار سینوسی رندوم می‌کشیم و محو می‌کنیم
            bg_plot_path = self.create_plot("np.sin(x) * x", "thumb_bg")
            if bg_plot_path:
                plot_img = Image.open(bg_plot_path).convert("RGBA")
                plot_img = plot_img.resize((width, height))
                # کم کردن شفافیت (Opacity)
                plot_img.putalpha(50) # عدد کمتر = محوتر
                img.paste(plot_img, (0, 0), plot_img)
                try: os.remove(bg_plot_path) 
                except: pass

            # 4. نوشتن تیتر با فونت درشت
            try:
                reshaped_text = arabic_reshaper.reshape(topic)
                bidi_text = get_display(reshaped_text)
            except:
                bidi_text = topic

            try:
                # فونت درشت‌تر برای کاور
                font = ImageFont.truetype("arial.ttf", 110)
            except:
                font = ImageFont.load_default()

            # محاسبه وسط‌چین
            text_bbox = draw.textbbox((0, 0), bidi_text, font=font)
            text_w = text_bbox[2] - text_bbox[0]
            text_h = text_bbox[3] - text_bbox[1]
            
            x = (width - text_w) / 2
            y = (height - text_h) / 2

            # رسم سایه متن (برای خوانایی بیشتر)
            draw.text((x+5, y+5), bidi_text, font=font, fill='black')
            
            # رسم خود متن (رنگ زرد یوتیوبی)
            draw.text((x, y), bidi_text, font=font, fill='#FFD700')

            # اضافه کردن برچسب "AI MATH" گوشه تصویر
            draw.rectangle([(0, 0), (250, 60)], fill='red')
            small_font = font.font_variant(size=40) if hasattr(font, 'font_variant') else font
            draw.text((20, 10), "AI MATH TUTOR", fill='white', font=small_font)

            # ذخیره
            filename = f"thumbnail_{project_id}.jpg"
            save_path = os.path.join(settings.MEDIA_ROOT, 'projects', filename)
            # اگر پوشه پروژه‌ها نبود، در ریشه مدیا بساز
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            img.save(save_path, quality=95)
            return save_path

        except Exception as e:
            print(f"خطا در ساخت کاور: {e}")
            return None