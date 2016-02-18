from django.contrib import admin
from .models import EmailRecord

@admin.register(EmailRecord)
class EmailRecordAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created_at')
    readonly_fields = fields = ('user', 'bills')
