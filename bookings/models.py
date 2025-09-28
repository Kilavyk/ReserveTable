from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from users.models import CustomUser
from tables.models import Table


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
        ('completed', 'Завершено'),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text="Пользователь, сделавший бронь"
    )

    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text="Столик для бронирования"
    )

    date = models.DateField(
        help_text="Дата посещения"
    )

    time = models.TimeField(
        help_text="Время посещения"
    )

    number_of_guests = models.PositiveSmallIntegerField(
        help_text="Количество гостей"
    )

    comment = models.TextField(
        blank=True,
        null=True,
        help_text="Комментарии к брони"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Статус бронирования"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Дата создания брони"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Дата последнего обновления"
    )

    def clean(self):
        from django.core.exceptions import ValidationError

        # Проверка: нельзя бронировать на прошедшую дату/время
        current_datetime = timezone.now()
        booking_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.time)
        )

        if booking_datetime < current_datetime:
            raise ValidationError('Нельзя бронировать на прошедшую дату/время.')

        # Проверка: количество гостей не должно превышать max_guests выбранного столика
        if self.number_of_guests > self.table.max_guests:
            raise ValidationError(
                f'Количество гостей ({self.number_of_guests}) превышает '
                f'максимальную вместимость столика ({self.table.max_guests}).'
            )

    def __str__(self):
        return f"Бронь {self.table.number} на {self.date} в {self.time} для {self.user.phone_number}"

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        unique_together = ('table', 'date', 'time')
        ordering = ['date', 'time']
