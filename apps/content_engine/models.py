from django.db import models

class VideoProject(models.Model):
    # ==========================
    # 1. تعریف انتخاب‌ها (Choices)
    # ==========================
    STATUS_CHOICES = [
        ('draft', 'پیش‌نویس'),
        ('script_ready', 'اسکریپت آماده'),
        ('audio_ready', 'صدا تولید شده'),
        ('video_ready', 'ویدیو نهایی ساخته شده'),
        ('uploaded', 'آپلود شده در برنامه'),
    ]

    PROJECT_TYPE_CHOICES = [
        ('topic_based', 'بر اساس موضوع (متن)'),
        ('image_based', 'بر اساس تصاویر (اسلاید)'),
    ]

    PLATFORM_CHOICES = [
        ('youtube', 'YouTube'),
        ('telegram', 'Telegram'),
        ('instagram', 'Instagram'),
        ('twitter', 'X (Twitter)'),
        ('tiktok', 'TikTok'),
    ]

    STYLE_CHOICES = [
        ('math', '👨‍🏫 معلم ریاضی (تخصصی)'),
        ('story', '📖 داستان‌گو (خلاقانه)'),
        ('business', '👔 رسمی و بیزنس (توضیحی)'),
        ('general', '🕵️ عمومی (توصیف ساده)'),
    ]

    DURATION_CHOICES = [
        ('short', 'کوتاه (۱ تا ۲ دقیقه)'),
        ('medium', 'متوسط (۳ تا ۵ دقیقه)'),
        ('long', 'طولانی و جامع (۵ تا ۱۰ دقیقه)'),
    ]

    # ==========================
    # 2. فیلدهای اصلی
    # ==========================
    topic = models.CharField(max_length=255, verbose_name="عنوان پروژه")
    
    platform = models.CharField(
        max_length=20, 
        choices=PLATFORM_CHOICES, 
        default='youtube',
        verbose_name="پلتفرم انتشار"
    )

    project_type = models.CharField(
        max_length=20,
        choices=PROJECT_TYPE_CHOICES,
        default='topic_based',
        verbose_name="نوع پروژه"
    )
    
    narrator_style = models.CharField(
        max_length=20, 
        choices=STYLE_CHOICES, 
        default='general', 
        verbose_name="سبک روایت"
    )

    duration_type = models.CharField(
        max_length=20,
        choices=DURATION_CHOICES,
        default='short',
        verbose_name="مدت زمان"
    )

    # ==========================
    # 3. زمان‌بندی و وضعیت
    # ==========================
    scheduled_creation = models.DateTimeField(null=True, blank=True, verbose_name="زمان شروع ساخت")
    scheduled_upload = models.DateTimeField(null=True, blank=True, verbose_name="زمان آپلود")
    
    status = models.CharField(
        max_length=50, 
        choices=STATUS_CHOICES, 
        default='draft',
        verbose_name="وضعیت فعلی"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    # ==========================
    # 4. محتوا و فایل‌ها
    # ==========================
    script_text = models.TextField(blank=True, null=True, verbose_name="متن سناریو")
    
    # مسیر فایل‌ها
    video_path = models.CharField(max_length=500, blank=True, null=True)
    thumbnail_path = models.CharField(max_length=500, blank=True, null=True)
    audio_path = models.CharField(max_length=500, blank=True, null=True)
    
    # سئو (SEO)
    generated_title = models.CharField(max_length=255, blank=True, null=True)
    generated_description = models.TextField(blank=True, null=True)
    generated_tags = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"[{self.get_platform_display()}] {self.topic}"

    class Meta:
        verbose_name = "پروژه ویدیویی"
        verbose_name_plural = "پروژه‌های ویدیویی"


class ProjectImage(models.Model):
    project = models.ForeignKey(VideoProject, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='user_uploads/', verbose_name="فایل تصویر")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['order']


from django.db import models

class VideoProject(models.Model):
    # ==========================
    # 1. تعریف انتخاب‌ها (Choices)
    # ==========================
    STATUS_CHOICES = [
        ('draft', 'پیش‌نویس'),
        ('script_ready', 'محتوا آماده'),
        ('video_ready', 'تصویر/ویدیو آماده'),
        ('uploaded', 'آپلود شده'),
    ]

    PROJECT_TYPE_CHOICES = [
        ('topic_based', 'ویدیو/متن معمولی'),
        ('image_based', 'ویدیو اسلایدی'),
        ('product_post', '🛍️ پست محصول (فروشگاهی)'),
    ]

    PLATFORM_CHOICES = [
        ('youtube', 'YouTube'),
        ('telegram', 'Telegram'),
        ('instagram', 'Instagram'),
        ('twitter', 'X (Twitter)'),
        ('tiktok', 'TikTok'),
    ]

    STYLE_CHOICES = [
        ('math', '👨‍🏫 معلم ریاضی'),
        ('story', '📖 داستان‌گو'),
        ('business', '👔 رسمی و بیزنس'),
        ('general', '🕵️ عمومی'),
        ('sales', '💰 بازاریاب حرفه‌ای'),
    ]

    DURATION_CHOICES = [
        ('short', 'کوتاه'),
        ('medium', 'متوسط'),
    ]

    # ==========================
    # 2. فیلدهای اصلی
    # ==========================
    topic = models.CharField(max_length=255, verbose_name="عنوان محصول / موضوع")
    
    platform = models.CharField(
        max_length=20, 
        choices=PLATFORM_CHOICES, 
        default='telegram',
        verbose_name="پلتفرم انتشار"
    )

    project_type = models.CharField(
        max_length=20,
        choices=PROJECT_TYPE_CHOICES,
        default='product_post',
        verbose_name="نوع پروژه"
    )
    
    narrator_style = models.CharField(
        max_length=20, 
        choices=STYLE_CHOICES, 
        default='sales', 
        verbose_name="سبک روایت"
    )

    duration_type = models.CharField(
        max_length=20,
        choices=DURATION_CHOICES,
        default='short',
        verbose_name="مدت زمان"
    )

    # ==========================
    # 3. فیلدهای مخصوص فروشگاه
    # ==========================
    brand_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="برند محصول")
    original_price = models.PositiveIntegerField(default=0, verbose_name="قیمت اصلی (تومان)")
    discount_percent = models.PositiveIntegerField(default=0, verbose_name="درصد تخفیف")
    shipping_info = models.CharField(max_length=100, default="3 تا 5 روز کاری", verbose_name="زمان ارسال")

    # ==========================
    # 4. سایر فیلدها
    # ==========================
    scheduled_creation = models.DateTimeField(null=True, blank=True, verbose_name="زمان شروع ساخت")
    scheduled_upload = models.DateTimeField(null=True, blank=True, verbose_name="زمان آپلود")
    
    status = models.CharField(
        max_length=50, 
        choices=STATUS_CHOICES, 
        default='draft',
        verbose_name="وضعیت فعلی"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    script_text = models.TextField(blank=True, null=True, verbose_name="متن کپشن/سناریو")
    
    # مسیر فایل‌ها
    video_path = models.CharField(max_length=500, blank=True, null=True)
    thumbnail_path = models.CharField(max_length=500, blank=True, null=True)
    audio_path = models.CharField(max_length=500, blank=True, null=True)
    
    # سئو (SEO)
    generated_title = models.CharField(max_length=255, blank=True, null=True)
    generated_description = models.TextField(blank=True, null=True)
    generated_tags = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.topic}"

    class Meta:
        verbose_name = "همه پروژه‌ها (کلی)"
        verbose_name_plural = "📂 آرشیو کل پروژه‌ها"

    def get_final_price(self):
        if self.original_price and self.discount_percent:
            discount_amount = (self.original_price * self.discount_percent) // 100
            return self.original_price - discount_amount
        return self.original_price
def get_upload_path(instance, filename):
   
    return f"{instance.project.platform}/{filename}"

class ProjectImage(models.Model):
    project = models.ForeignKey(VideoProject, related_name='images', on_delete=models.CASCADE)
    
    # استفاده از تابع جدید در upload_to
    image = models.ImageField(upload_to=get_upload_path, verbose_name="فایل تصویر")
    
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['order']
    class Meta: ordering = ['order']

# =========================================================
#  مدل‌های پروکسی (برای تفکیک در پنل ادمین)
# =========================================================

class YouTubeProject(VideoProject):
    class Meta:
        proxy = True # یعنی جدول جدید نساز، فقط نمایش را عوض کن
        verbose_name = "ویدیو یوتیوب"
        verbose_name_plural = "🔴 مدیریت یوتیوب"

class TelegramProject(VideoProject):
    class Meta:
        proxy = True
        verbose_name = "پست تلگرام"
        verbose_name_plural = "✈️ مدیریت تلگرام"

class InstagramProject(VideoProject):
    class Meta:
        proxy = True
        verbose_name = "ریلز اینستاگرام"
        verbose_name_plural = "📸 مدیریت اینستاگرام"