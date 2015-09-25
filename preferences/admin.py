from django.contrib import admin
from .models import Preferences


@admin.register(Preferences)
class PreferencesAdmin(admin.ModelAdmin):
    model = Preferences
