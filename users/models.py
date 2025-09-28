from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Номер телефона обязателен')

        phone_number = self.normalize_phone_number(phone_number)
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True')

        return self.create_user(phone_number, password, **extra_fields)

    def normalize_phone_number(self, phone_number):
        # Удаляем все символы кроме цифр
        normalized = ''.join(filter(str.isdigit, phone_number))
        # Добавляем +7 если номер российский и начинается с 7 или 8
        if len(normalized) == 11 and normalized.startswith('8'):
            normalized = '7' + normalized[1:]
        if len(normalized) == 10 and not normalized.startswith('7'):
            normalized = '7' + normalized
        if len(normalized) == 11 and not normalized.startswith('7'):
            normalized = '7' + normalized

        return '+' + normalized


class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{10,15}$',
        message="Номер телефона должен быть в формате: '+79991234567'. Допускается от 10 до 15 цифр."
    )

    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        unique=True,
        help_text="Введите номер телефона в формате +79991234567"
    )

    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)

    photo = models.ImageField(
        upload_to='users/photos/',
        blank=True,
        null=True,
        help_text="Фотография пользователя"
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'  # Используем номер телефона для входа
    REQUIRED_FIELDS = []  # Другие обязательные поля при создании суперпользователя

    def __str__(self):
        return f"{self.phone_number} ({self.get_full_name()})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
