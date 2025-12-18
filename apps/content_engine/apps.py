from django.apps import AppConfig

class ContentEngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # مسیر صحیح اپلیکیشن شما
    name = 'apps.content_engine' 
    verbose_name = 'موتور محتوا'
