import os
import socket  # <--- کتابخانه استاندارد برای تنظیم تایم‌اوت
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from django.conf import settings

# تنظیم زمان انتظار روی ۱۰۰۰ ثانیه (حدود ۱۶ دقیقه) برای کل برنامه
socket.setdefaulttimeout(1000)

class YouTubeUploader:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
        self.CLIENT_SECRETS_FILE = os.path.join(settings.BASE_DIR, 'client_secrets.json')
        self.TOKEN_FILE = os.path.join(settings.BASE_DIR, 'token.json')

    def get_authenticated_service(self):
        creds = None
        # تلاش برای خواندن توکن قبلی
        if os.path.exists(self.TOKEN_FILE):
            try:
                creds = Credentials.from_authorized_user_file(self.TOKEN_FILE, self.SCOPES)
            except:
                os.remove(self.TOKEN_FILE)
                creds = None
        
        # اگر توکن معتبر نیست، لاگین کن
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except:
                    creds = None
            
            if not creds:
                if not os.path.exists(self.CLIENT_SECRETS_FILE):
                    raise FileNotFoundError("فایل client_secrets.json پیدا نشد!")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CLIENT_SECRETS_FILE, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # ذخیره توکن
            with open(self.TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())

        # ساخت سرویس (بدون آرگومان‌های اضافه که باعث خطا می‌شد)
        return build('youtube', 'v3', credentials=creds)

    def upload_video(self, video_path, title, description):
        try:
            youtube = self.get_authenticated_service()
            print(f"--- شروع آپلود: {title} ---")

            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': ['AI', 'Education', 'Math'],
                    'categoryId': '27' # دسته بندی آموزش
                },
                'status': {
                    'privacyStatus': 'private', # خصوصی
                    'selfDeclaredMadeForKids': False
                }
            }

            # آماده‌سازی فایل (با قابلیت ادامه دادن در صورت قطعی)
            media = MediaFileUpload(video_path, chunksize=1024*1024, resumable=True)

            request = youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )

            # حلقه آپلود
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"وضعیت آپلود: {int(status.progress() * 100)}%")

            print("✅ آپلود تمام شد! شناسه:", response.get('id'))
            return response.get('id')

        except Exception as e:
            print(f"--- خطا در سرویس آپلود: {e} ---")
            return None