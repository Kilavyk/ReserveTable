from django.contrib import admin
from django.utils.html import format_html
from .models import Category, MenuItem


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'menu_items_count']
    list_editable = ['order']
    search_fields = ['name']

    def menu_items_count(self, obj):
        return obj.menuitem_set.count()

    menu_items_count.short_description = 'Количество позиций'


class MenuItemAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'category',
        'dish_type',
        'price',
        'weight_volume',
        'is_available',
        'image_preview'
    ]
    list_editable = ['price', 'is_available']
    list_filter = ['category', 'dish_type', 'is_available']
    search_fields = ['name', 'description', 'ingredients']

    def weight_volume(self, obj):
        if obj.weight:
            return f"{obj.weight} г"
        elif obj.volume:
            return f"{obj.volume} мл"
        return "-"

    weight_volume.short_description = 'Вес/Объем'

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.image.url
            )
        return "—"

    image_preview.short_description = 'Изображение'


admin.site.register(Category, CategoryAdmin)
admin.site.register(MenuItem, MenuItemAdmin)
