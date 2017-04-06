from django.contrib import admin

from .models import Blog


@admin.register(Blog)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published')
