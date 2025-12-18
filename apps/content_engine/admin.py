from django.contrib import admin
from django.contrib import messages
from django.shortcuts import redirect
from .models import VideoProject, ProjectImage, YouTubeProject, TelegramProject, InstagramProject

# --- اکشن اختصاصی: ارسال به هوش مصنوعی ---
def run_ai_generation(modeladmin, request, queryset):
    """
    این اکشن، پروژه‌های انتخاب شده را به صف هوش مصنوعی می‌فرستد.
    دقیقاً مثل دکمه 'ساخت ویدیو' در داشبورد عمل می‌کند.
    """
    for project in queryset:
        # هدایت به ویوی ساخت ویدیو در داشبورد
        # (این کار باعث می‌شود لاجیک داشبورد اجرا شود)
        return redirect('start_generation', project_id=project.id)

run_ai_generation.short_description = "🤖 ارسال به هوش مصنوعی (ساخت محتوا)"


# تنظیمات عکس‌ها (فقط داخل پروژه دیده شود، نه در منوی اصلی)
class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ('image', 'order')

# ما مدل ProjectImage را رجیستر نمی‌کنیم تا از منوی اصلی حذف شود
# admin.site.register(ProjectImage) <--- این خط حذف شد


# =========================================================
# 1. ادمین اختصاصی یوتیوب
# =========================================================
@admin.register(YouTubeProject)
class YouTubeAdmin(admin.ModelAdmin):
    # اکشن‌ها: حذف (پیش‌فرض) + هوش مصنوعی
    actions = [run_ai_generation]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(platform='youtube')

    def save_model(self, request, obj, form, change):
        obj.platform = 'youtube'
        super().save_model(request, obj, form, change)

    list_display = ('topic', 'status', 'created_at')
    inlines = [ProjectImageInline]

    fieldsets = (
        ('اطلاعات ویدیو', {
            'fields': ('topic', 'project_type', 'status', 'narrator_style', 'duration_type')
        }),
        ('سناریو و متن', {
            'fields': ('script_text',)
        }),
        ('خروجی‌ها', {
            'fields': ('video_path', 'thumbnail_path')
        }),
        ('سئو (SEO)', {
            'fields': ('generated_title', 'generated_description', 'generated_tags'),
            'classes': ('collapse',),
        }),
    )

# =========================================================
# 2. ادمین اختصاصی تلگرام (مرتب‌سازی شده)
# =========================================================
@admin.register(TelegramProject)
class TelegramAdmin(admin.ModelAdmin):
    actions = [run_ai_generation]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(platform='telegram')

    def save_model(self, request, obj, form, change):
        obj.platform = 'telegram'
        super().save_model(request, obj, form, change)

    list_display = ('topic', 'brand_name', 'price_display', 'status')
    inlines = [ProjectImageInline]

    # --- چیدمان فرم ویرایش (طبق دستور شما) ---
    fieldsets = (
        ('📦 مشخصات محصول (اصلی)', {
            'fields': (
                'topic',           # نام محصول
                'brand_name',      # برند
                'original_price',  # قیمت
                'discount_percent',# تخفیف
                'shipping_info',   # ارسال
                'project_type',    # نوع پست
                'status'           # وضعیت
            ),
            'description': 'اطلاعات ویترین فروشگاه را اینجا وارد کنید.'
        }),
        ('✍️ تولید محتوا (هوش مصنوعی)', {
            'fields': ('narrator_style', 'script_text'),
        }),
        ('🖼️ فایل‌های نهایی', {
            'fields': ('thumbnail_path', 'video_path'),
        }),
        ('🔍 سئو و هشتگ‌ها', {
            'fields': ('generated_title', 'generated_description', 'generated_tags'),
            'classes': ('collapse',),
        }),
    )

    def price_display(self, obj):
        if obj.original_price: return f"{obj.original_price:,}"
        return "-"
    price_display.short_description = "قیمت (تومان)"


# =========================================================
# 3. ادمین اینستاگرام
# =========================================================
@admin.register(InstagramProject)
class InstagramAdmin(admin.ModelAdmin):
    actions = [run_ai_generation]
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(platform='instagram')
    
    def save_model(self, request, obj, form, change):
        obj.platform = 'instagram'
        super().save_model(request, obj, form, change)
        
    list_display = ('topic', 'status')
    fieldsets = (
        ('Reels Info', {'fields': ('topic', 'status', 'video_path')}),
    )