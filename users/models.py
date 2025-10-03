from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
import secrets


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True,
        verbose_name="Email"
    )

    first_name = models.CharField(max_length=30, blank=True, verbose_name="Имя")
    last_name = models.CharField(max_length=30, blank=True, verbose_name="Фамилия")

    photo = models.ImageField(
        upload_to='users/photos/',
        blank=True,
        null=True,
        verbose_name="Фотография",
        help_text="Фотография пользователя"
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Поля для верификации email
    verification_token = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Токен верификации"
    )

    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  # Используем email для входа
    REQUIRED_FIELDS = []  # Другие обязательные поля при создании суперпользователя

    def __str__(self):
        return f"{self.email} ({self.get_full_name()})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    def generate_verification_token(self):
        """Генерирует токен для верификации email"""
        self.verification_token = secrets.token_hex(16)
        self.save()
        return self.verification_token

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
