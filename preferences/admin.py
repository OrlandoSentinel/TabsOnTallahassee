from django.contrib import admin

# Register your models here.

from .models import Preferences, PersonFollow, TopicFollow, LocationFollow

admin.site.register(Preferences)
admin.site.register(PersonFollow)
