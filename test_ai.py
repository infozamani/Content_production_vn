import google.generativeai as genai
import os
from dotenv import load_dotenv

# لود کردن فایل .env
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

print(f"🔑 کلید شما: {api_key[:10]}...")

if not api_key:
    print("❌ خطا: کلید GOOGLE_API_KEY در فایل .env پیدا نشد.")
else:
    try:
        genai.configure(api_key=api_key)
        
        # دقیقاً مدلی که شما گفتید کار می‌کند
        model_name = 'gemini-2.5-flash' 
        print(f"⏳ در حال تست مدل {model_name}...")
        
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("سلام! خودت را در یک جمله معرفی کن.")
        
        print("\n✅ موفقیت! پاسخ هوش مصنوعی:")
        print(response.text)
        
    except Exception as e:
        print("\n❌ خطا:")
        print(e)
        print("\n💡 راهنمایی: اگر خطای 404 داد، یعنی نام مدل دقیق نیست.")
        print("💡 اگر خطای 403 داد، یعنی کلید مشکل دارد یا تحریم است.")