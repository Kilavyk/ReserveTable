# Bookings/models.py
from django.db import models
from django.conf import settings # Используем настройки проекта для User
from tables.models import Table # Импортируем модель Table из приложения tables
from datetime import datetime # Для валидации даты

class Booking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Подтверждено'),
        ('pending', 'В ожидании'),
        ('cancelled', 'Отменено'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Ссылка на кастомную модель пользователя
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text="Пользователь, сделавший бронирование"
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text="Забронированный столик"
    )
    booking_date = models.DateField(
        help_text="Дата бронирования"
    )
    booking_time = models.TimeField(
        help_text="Время бронирования"
    )
    guests_count = models.PositiveSmallIntegerField(
        help_text="Количество гостей"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Статус бронирования"
    )
    special_requests = models.TextField(
        blank=True,
        null=True,
        help_text="Особые пожелания"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Бронь {self.id} - {self.table.number} на {self.booking_date} в {self.booking_time}"

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-created_at']
        unique_together = ('table', 'booking_date', 'booking_time') # Один столик не может быть забронирован дважды на одно и то же время

    def is_past(self):
        """Проверяет, прошло ли бронирование."""
        if self.booking_date < datetime.now().date():
            return True
        elif self.booking_date == datetime.now().date() and self.booking_time < datetime.now().time():
            return True
        return False