# python create_administrator_group.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from bookings.models import Booking
from tables.models import Table
from users.models import CustomUser


def create_administrator_group():
    """Создает группу модераторов с необходимыми правами"""

    # Создаем или получаем группу
    group, created = Group.objects.get_or_create(name='Администраторы')

    if created:
        print("Группа 'Администраторы' создана успешно!")
    else:
        print("Группа 'Администраторы' уже существует!")

    # Получаем разрешения для моделей
    booking_content_type = ContentType.objects.get_for_model(Booking)
    table_content_type = ContentType.objects.get_for_model(Table)
    user_content_type = ContentType.objects.get_for_model(CustomUser)

    # Добавляем разрешения для бронирований
    booking_permissions = Permission.objects.filter(
        content_type=booking_content_type,
        codename__in=[
            'add_booking', 'change_booking', 'delete_booking', 'view_booking'
        ]
    )

    # Добавляем разрешения для столиков
    table_permissions = Permission.objects.filter(
        content_type=table_content_type,
        codename__in=['view_table']
    )

    # Добавляем разрешения для пользователей
    user_permissions = Permission.objects.filter(
        content_type=user_content_type,
        codename__in=['view_customuser']
    )

    # Добавляем все разрешения в группу
    all_permissions = list(booking_permissions) + list(table_permissions) + list(user_permissions)
    group.permissions.set(all_permissions)

    print(f"Добавлено {len(all_permissions)} разрешений в группу 'Модераторы'")

    # Выводим список всех добавленных разрешений
    print("\nДобавленные разрешения:")
    for perm in all_permissions:
        print(f"  - {perm.name} ({perm.codename})")

    return group


if __name__ == '__main__':
    create_administrator_group()
