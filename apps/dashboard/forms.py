from django import forms
from apps.content_engine.models import VideoProject

class VideoProjectForm(forms.ModelForm):
    class Meta:
        model = VideoProject
        fields = [
            'topic', 'project_type', 'narrator_style', 'duration_type',
            'brand_name', 'original_price', 'discount_percent', 'shipping_info', # فیلدهای فروشگاه
            'script_text', # فیلد متن برای ویرایش کپشن
            'scheduled_creation', 'scheduled_upload' # زمان‌بندی
        ]
        
        widgets = {
            'topic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عنوان محصول یا موضوع ویدیو...'}),
            'project_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_project_type'}),
            'narrator_style': forms.Select(attrs={'class': 'form-select'}),
            'duration_type': forms.Select(attrs={'class': 'form-select'}),
            
            # --- فیلدهای فروشگاهی ---
            'brand_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام برند (مثلاً Nike)'}),
            'original_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'تومان'}),
            'discount_percent': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'درصد %'}),
            'shipping_info': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثلاً: ارسال رایگان'}),

            # --- فیلد متن (کپشن) برای مشاهده و ویرایش ---
            'script_text': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 6, 
                'placeholder': 'متن کپشن یا سناریو اینجا نمایش داده می‌شود...'
            }),

            # --- زمان‌بندی ---
            'scheduled_creation': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'scheduled_upload': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
        
        labels = {
            'topic': 'عنوان / نام محصول',
            'project_type': 'نوع پست',
            'brand_name': '🏷️ برند',
            'original_price': '💰 قیمت اصلی',
            'discount_percent': '🔥 تخفیف (%)',
            'shipping_info': '🚚 شرایط ارسال',
            'script_text': '✍️ متن کپشن / سناریو (قابل ویرایش)',
            'scheduled_creation': '⏰ زمان شروع ساخت',
            'scheduled_upload': '🚀 زمان آپلود خودکار',
        }