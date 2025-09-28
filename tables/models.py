from django.db import models


class Table(models.Model):
    number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Номер столика"
    )

    max_guests = models.PositiveSmallIntegerField(
        help_text="Максимальное количество гостей (до 10)",
        choices=[(i, i) for i in range(1, 11)]
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Статус столика (активен/неактивен)"
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text="Описание столика"
    )

    def __str__(self):
        return f"Столик {self.number}"

    class Meta:
        verbose_name = 'Столик'
        verbose_name_plural = 'Столики'
        ordering = ['number']
