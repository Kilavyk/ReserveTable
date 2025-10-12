from datetime import datetime, time

from django.conf import settings
from django.db import models

from tables.models import Table


class Booking(models.Model):
    STATUS_CHOICES = [
        ("confirmed", "Подтверждено"),
        ("pending", "В ожидании"),
        ("cancelled", "Отменено"),
    ]

    # Временные слоты ресторана
    TIME_SLOTS = [
        (time(12, 0), "12:00 - 14:00"),
        (time(14, 0), "14:00 - 16:00"),
        (time(16, 0), "16:00 - 18:00"),
        (time(18, 0), "18:00 - 20:00"),
        (time(20, 0), "20:00 - 22:00"),
        (time(22, 0), "22:00 - 00:00"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
        help_text="Пользователь, сделавший бронирование",
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        related_name="bookings",
        help_text="Забронированный столик",
    )
    booking_date = models.DateField(help_text="Дата бронирования")
    time_slot = models.TimeField(
        choices=TIME_SLOTS, help_text="Временной слот бронирования"
    )
    guests_count = models.PositiveSmallIntegerField(help_text="Количество гостей")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        help_text="Статус бронирования",
    )
    special_requests = models.TextField(
        blank=True, null=True, help_text="Особые пожелания"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Бронь {self.id} - {self.table.number} на {self.booking_date} в {self.time_slot}"

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["table", "booking_date", "time_slot"],
                condition=models.Q(status__in=["confirmed", "pending"]),
                name="unique_active_booking_per_table_timeslot",
            )
        ]

    def get_time_slot_display(self):
        """Возвращает отображаемое значение временного слота"""
        for slot_value, slot_display in self.TIME_SLOTS:
            if slot_value == self.time_slot:
                return slot_display
        return str(self.time_slot)

    def is_past(self):
        """Проверяет, прошло ли бронирование."""
        if self.booking_date < datetime.now().date():
            return True
        elif (
            self.booking_date == datetime.now().date()
            and self.time_slot < datetime.now().time()
        ):
            return True
        return False
