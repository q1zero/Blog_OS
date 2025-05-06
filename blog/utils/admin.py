from django.contrib import admin
from .models import SensitiveWord


@admin.register(SensitiveWord)
class SensitiveWordAdmin(admin.ModelAdmin):
    list_display = ("word", "created_at")
    search_fields = ("word",)


# Register your models here.
