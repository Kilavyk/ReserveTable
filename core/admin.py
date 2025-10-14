from django.contrib import admin
from django.utils.html import format_html

from .models import SiteContent


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = (
        "content_type_display",
        "content_preview",
        "is_active",
        "updated_at",
    )
    list_editable = ("is_active",)
    list_filter = ("content_type", "is_active", "updated_at")
    search_fields = ("title", "content", "content_type")
    readonly_fields = ("updated_at", "content_type_display")
    fieldsets = (
        (
            "Основная информация",
            {"fields": ("content_type_display", "content_type", "is_active")},
        ),
        (
            "Содержание",
            {
                "fields": ("title", "content"),
                "description": "Заголовок можно оставить пустым, если он не нужен",
            },
        ),
        ("Системная информация", {"fields": ("updated_at",), "classes": ("collapse",)}),
    )

    def content_type_display(self, obj):
        return obj.get_content_type_display()

    content_type_display.short_description = "Тип контента"

    def content_preview(self, obj):
        preview = obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
        return format_html('<span title="{}">{}</span>', obj.content, preview)

    content_preview.short_description = "Превью содержания"

    def get_readonly_fields(self, request, obj=None):
        if obj:  # редактирование существующего объекта
            return self.readonly_fields + ("content_type",)
        return self.readonly_fields

    def get_fieldsets(self, request, obj=None):
        if not obj:  # создание нового объекта
            return (
                ("Основная информация", {"fields": ("content_type", "is_active")}),
                ("Содержание", {"fields": ("title", "content")}),
            )
        return super().get_fieldsets(request, obj)
