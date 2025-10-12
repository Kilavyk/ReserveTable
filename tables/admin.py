from django.contrib import admin
from .models import Table


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    """Админ-панель для управления столиками"""

    list_display = [
        'number',
        'max_guests',
        'is_active',
        'get_current_bookings_count',
        'get_future_bookings_count'
    ]

    list_filter = [
        'is_active',
        'max_guests'
    ]

    search_fields = [
        'number',
        'description'
    ]

    list_editable = ['is_active']

    fieldsets = [
        ('Основная информация', {
            'fields': [
                'number',
                'max_guests',
                'is_active'
            ]
        }),
        ('Дополнительная информация', {
            'fields': [
                'description'
            ],
            'classes': ['collapse']
        }),
    ]

    def get_current_bookings_count(self, obj):
        """Количество активных бронирований на сегодня"""
        from django.utils import timezone
        from bookings.models import Booking

        today = timezone.now().date()
        return Booking.objects.filter(
            table=obj,
            booking_date=today,
            status__in=['confirmed', 'pending']
        ).count()

    get_current_bookings_count.short_description = 'Броней на сегодня'

    def get_future_bookings_count(self, obj):
        """Количество будущих бронирований"""
        from django.utils import timezone
        from bookings.models import Booking

        today = timezone.now().date()
        return Booking.objects.filter(
            table=obj,
            booking_date__gte=today,
            status__in=['confirmed', 'pending']
        ).count()

    get_future_bookings_count.short_description = 'Всего будущих броней'

    def get_queryset(self, request):
        """Оптимизация запроса к БД"""
        return super().get_queryset(request)

    actions = ['activate_tables', 'deactivate_tables']

    def activate_tables(self, request, queryset):
        """Активировать выбранные столики"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} столиков активировано')

    activate_tables.short_description = "Активировать выбранные столики"

    def deactivate_tables(self, request, queryset):
        """Деактивировать выбранные столики"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} столиков деактивировано')

    deactivate_tables.short_description = "Деактивировать выбранные столики"

    def bookings_count(self, obj):
        return obj.bookings.count()
    bookings_count.short_description = 'Количество бронирований'
