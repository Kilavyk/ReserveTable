from django.db import models
from django.core.validators import MinValueValidator


class Category(models.Model):
    """Модель категорий меню"""
    name = models.CharField(
        max_length=100,
        verbose_name='Название категории'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок отображения'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    """Модель блюда/напитка в меню"""

    DISH_TYPE_CHOICES = [
        ('food', 'Блюдо'),
        ('drink', 'Напиток'),
    ]

    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория'
    )
    dish_type = models.CharField(
        max_length=10,
        choices=DISH_TYPE_CHOICES,
        default='food',
        verbose_name='Тип'
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Цена'
    )
    weight = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Вес (гр)'
    )
    volume = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Объем (мл)'
    )
    ingredients = models.TextField(
        blank=True,
        verbose_name='Ингредиенты'
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name='Доступно'
    )
    image = models.ImageField(
        upload_to='menu_items/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )

    class Meta:
        verbose_name = 'Позиция меню'
        verbose_name_plural = 'Позиции меню'
        ordering = ['category__order', 'name']

    def __str__(self):
        return f"{self.name} - {self.price} руб."
