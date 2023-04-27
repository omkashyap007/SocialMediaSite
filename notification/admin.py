from django.contrib import admin
from notification.models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_filter = ["content_type"]
    list_display = ["target" , "content_type" , "timestamp"]
    search_fields = ["target__username" , "target__email"]
        
    class Meta :
        model = Notification