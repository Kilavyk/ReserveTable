# python create_tables.py

import os
import sys
import django
from tables.models import Table

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()


def create_tables():
    """Создает и сохраняет несколько столиков в базу данных."""
    # Пример данных для создания столиков
    table_data = [
        {"number": "1", "max_guests": 2, "description": "Уютный столик у окна с видом на парк"},
        {"number": "2", "max_guests": 4, "description": "Комфортный столик в центре зала"},
        {"number": "3", "max_guests": 6, "description": "Просторный столик для компании друзей"},
        {"number": "4", "max_guests": 8, "description": "Большой семейный столик с мягкими диванами"},
        {"number": "5", "max_guests": 10, "description": "Банкетный столик для торжественных мероприятий"},
        {"number": "6", "max_guests": 2, "description": "Романтический столик в уединенном уголке"},
        {"number": "7", "max_guests": 4, "description": "Столик у камина с теплой атмосферой"},
        {"number": "8", "max_guests": 6, "description": "Столик на террасе с видом на город"},
    ]

    created_count = 0
    updated_count = 0

    for data in table_data:
        # Проверяем, существует ли уже столик с таким номером
        try:
            table = Table.objects.get(number=data["number"])
            # Если существует, обновляем данные
            table.max_guests = data["max_guests"]
            table.description = data["description"]
            table.is_active = True
            table.save()
            print(f"Обновлен столик: {table}")
            updated_count += 1
        except Table.DoesNotExist:
            # Если не существует, создаем новый
            table = Table.objects.create(
                number=data["number"],
                max_guests=data["max_guests"],
                description=data["description"],
                is_active=True
            )
            print(f"Создан столик: {table}")
            created_count += 1

    print(f"\nИтог: создано {created_count} новых столиков, обновлено {updated_count} столиков.")

    # Выводим общую информацию о созданных столиках
    total_tables = Table.objects.count()
    active_tables = Table.objects.filter(is_active=True).count()
    print(f"Всего столиков в базе: {total_tables}")
    print(f"Активных столиков: {active_tables}")


if __name__ == "__main__":
    create_tables()
