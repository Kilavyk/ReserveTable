from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.contrib import messages
from django.shortcuts import redirect
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'table_number',
        'user_email',
        'booking_date',
        'time_slot_display',
        'guests_count',
        'status_display',
        'is_past_display',
        'admin_actions'  # Переименовано с actions
    ]

    list_filter = [
        'status',
        'booking_date',
        'time_slot',
        'table'
    ]

    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
        'table__number'
    ]

    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'table', 'booking_date', 'time_slot', 'guests_count', 'status')
        }),
        ('Дополнительная информация', {
            'fields': ('special_requests', 'created_at', 'updated_at')
        }),
    )

    def table_number(self, obj):
        return f"Столик {obj.table.number}"

    table_number.short_description = 'Столик'

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'Пользователь'

    def time_slot_display(self, obj):
        return obj.get_time_slot_display()

    time_slot_display.short_description = 'Время'

    def status_display(self, obj):
        status_colors = {
            'confirmed': 'green',
            'pending': 'orange',
            'cancelled': 'red'
        }
        color = status_colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )

    status_display.short_description = 'Статус'

    def is_past_display(self, obj):
        if obj.is_past():
            return format_html("Прошедшее")
        return format_html("Активное")

    is_past_display.short_description = 'Активность'

    def admin_actions(self, obj):  # Переименовано с actions
        links = []
        if obj.status != 'confirmed' and not obj.is_past():
            confirm_url = reverse('admin:bookings_booking_confirm', args=[obj.id])
            links.append(f'<a href="{confirm_url}"">Подтвердить</a>')

        if obj.status != 'cancelled' and not obj.is_past():
            cancel_url = reverse('admin:bookings_booking_cancel', args=[obj.id])
            links.append(f'<a href="{cancel_url}"">Отменить</a>')

        return format_html(' | '.join(links)) if links else '-'

    admin_actions.short_description = 'Действия'  # Обновлено описание

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/confirm/',
                self.admin_site.admin_view(self.confirm_booking),
                name='bookings_booking_confirm',
            ),
            path(
                '<path:object_id>/cancel/',
                self.admin_site.admin_view(self.cancel_booking),
                name='bookings_booking_cancel',
            ),
        ]
        return custom_urls + urls

    def confirm_booking(self, request, object_id):
        booking = Booking.objects.get(id=object_id)
        booking.status = 'confirmed'
        booking.save()

        messages.success(
            request,
            f'Бронирование столика {booking.table.number} подтверждено!'
        )
        return redirect('admin:bookings_booking_changelist')

    def cancel_booking(self, request, object_id):
        booking = Booking.objects.get(id=object_id)
        booking.status = 'cancelled'
        booking.save()

        messages.success(
            request,
            f'Бронирование столика {booking.table.number} отменено!'
        )
        return redirect('admin:bookings_booking_changelist')

    # Разрешаем создание бронирований без подтверждения для администраторов
    def save_model(self, request, obj, form, change):
        if not change:  # Если это новое бронирование
            obj.status = 'confirmed'  # Автоматически подтверждаем
        super().save_model(request, obj, form, change)
