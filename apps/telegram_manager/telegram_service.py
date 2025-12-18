import requests
import os

class TelegramUploader:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHANNEL_ID")
        self.base_url = f"https://api.telegram.org/bot{self.token}/"

    def send_video(self, video_path, caption=""):
        """
        ارسال ویدیو به کانال تلگرام
        """
        if not self.token or not self.chat_id:
            print("❌ تنظیمات تلگرام (Token/ID) یافت نشد.")
            return None

        method = "sendVideo"
        url = self.base_url + method
        
        try:
            print(f"🚀 در حال ارسال ویدیو به تلگرام: {video_path}...")
            
            with open(video_path, 'rb') as video_file:
                files = {'video': video_file}
                data = {
                    'chat_id': self.chat_id,
                    'caption': caption,
                    'parse_mode': 'HTML' # برای پشتیبانی از بولد و لینک
                }
                
                # ارسال درخواست (تایم‌اوت ۶۰ ثانیه برای ویدیوهای حجیم)
                response = requests.post(url, files=files, data=data, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ ارسال به تلگرام موفق بود.")
                return result.get('result', {}).get('message_id')
            else:
                print(f"❌ خطا در تلگرام: {response.text}")
                return None

        except Exception as e:
            print(f"❌ خطای اتصال تلگرام: {e}")
            return None

    def send_photo(self, photo_path, caption=""):
        """
        ارسال عکس (کاور) به تلگرام
        """
        if not self.token: return None
        url = self.base_url + "sendPhoto"
        try:
            with open(photo_path, 'rb') as img:
                files = {'photo': img}
                data = {'chat_id': self.chat_id, 'caption': caption, 'parse_mode': 'HTML'}
                requests.post(url, files=files, data=data)
        except: pass