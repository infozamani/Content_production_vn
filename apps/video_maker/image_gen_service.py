# این فایل اصلاح شد تا وقتی کلید ندارید، ارور ندهد و سیستم را متوقف نکند.
class ImageGenerator:
    def __init__(self):
        # ما اینجا وانمود می‌کنیم که کلاینت نداریم
        # تا ویدیو ساز (video_service) بفهمد باید برود سراغ روش رایگان
        self.client = None 

    def generate_image(self, prompt, project_id):
        # همیشه None برمی‌گردانیم
        # این باعث می‌شود video_service به خط "سوییچ به حالت رایگان" برود
        return None