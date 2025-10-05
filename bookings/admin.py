from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Админ-панель для управления бронированиями"""

    list_display = [
        'id',
        'user',
        'table',
        'booking_date',
        'get_time_slot_display',
        'guests_count',
        'status',
        'created_at'
    ]

    list_filter = [
        'status',
        'booking_date',
        'time_slot',
        'table',
        'created_at'
    ]

    search_fields = [
        'user__username',
        'user__email',
        'table__number',
        'special_requests'
    ]

    readonly_fields = ['created_at', 'updated_at']

    fieldsets = [
        ('Основная информация', {
            'fields': [
                'user',
                'table',
                'booking_date',
                'time_slot',
                'guests_count',
                'status'
            ]
        }),
        ('Дополнительная информация', {
            'fields': [
                'special_requests',
                'created_at',
                'updated_at'
            ]
        }),
    ]

    def get_time_slot_display(self, obj):
        """Отображает временной слот в читаемом формате"""
        return obj.get_time_slot_display()

    get_time_slot_display.short_description = 'Временной слот'

    def get_queryset(self, request):
        """Оптимизация запроса к БД"""
        return super().get_queryset(request).select_related('user', 'table')