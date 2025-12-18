import google.generativeai as genai
import os

# کلید خود را اینجا تنظیم کنید
os.environ["GOOGLE_API_KEY"] = "AIzaSyDBnqIGnrhcXoXEXU9fqXXW1NUAUMC7Owc" # کلید کامل خود را اینجا بگذارید
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# ایجاد مدل
model = genai.GenerativeModel('gemini-2.5-flash') # یا gemini-2.0-flash-exp اگر دسترسی دارید

response = model.generate_content("سلام، خودت را معرفی کن")

print(response.text)