# python create_sample_menu.py

import os
import sys

import django

from victuals.models import Category, MenuItem

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django.setup()


def create_sample_menu():
    """Создает пример меню для ресторана"""

    print("Создание категорий...")

    # Создаем категории
    categories_data = [
        {"name": "Холодные закуски", "order": 1},
        {"name": "Салаты", "order": 2},
        {"name": "Супы", "order": 3},
        {"name": "Горячие блюда", "order": 4},
        {"name": "Гарниры", "order": 5},
        {"name": "Десерты", "order": 6},
        {"name": "Горячие напитки", "order": 7},
        {"name": "Холодные напитки", "order": 8},
        {"name": "Алкогольные напитки", "order": 9},
    ]

    categories = {}
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data["name"], defaults={"order": cat_data["order"]}
        )
        categories[cat_data["name"]] = category
        print(f"Категория: {category.name}")

    print("\nСоздание позиций меню...")

    # Позиции меню
    menu_items_data = [
        # Холодные закуски
        {
            "name": "Брускетта с томатами",
            "description": "Хрустящий хлеб с свежими томатами, базиликом и оливковым маслом",
            "category": categories["Холодные закуски"],
            "dish_type": "food",
            "price": 350,
            "weight": 150,
            "ingredients": "Хлеб, помидоры, базилик, чеснок, оливковое масло",
            "is_available": True,
        },
        {
            "name": "Сырная тарелка",
            "description": "Ассортимент из трех видов сыров с орехами и медом",
            "category": categories["Холодные закуски"],
            "dish_type": "food",
            "price": 580,
            "weight": 200,
            "ingredients": "Дор блю, Гауда, Бри, грецкие орехи, мед",
            "is_available": True,
        },
        # Салаты
        {
            "name": "Греческий салат",
            "description": "Классический салат с сыром фета, оливками и свежими овощами",
            "category": categories["Салаты"],
            "dish_type": "food",
            "price": 420,
            "weight": 300,
            "ingredients": "Помидоры, огурцы, перец, лук, сыр фета, оливки, оливковое масло",
            "is_available": True,
        },
        {
            "name": "Цезарь с курицей",
            "description": "Салат с листьями айсберг, куриной грудкой, пармезаном и соусом цезарь",
            "category": categories["Салаты"],
            "dish_type": "food",
            "price": 480,
            "weight": 350,
            "ingredients": "Айсберг, куриное филе, пармезан, крутоны, соус цезарь",
            "is_available": True,
        },
        # Супы
        {
            "name": "Том Ям",
            "description": "Острый тайский суп с креветками и кокосовым молоком",
            "category": categories["Супы"],
            "dish_type": "food",
            "price": 520,
            "weight": 400,
            "ingredients": "Креветки, грибы, лемонграсс, кокосовое молоко, чили, лайм",
            "is_available": True,
        },
        {
            "name": "Борщ",
            "description": "Традиционный украинский борщ со сметаной",
            "category": categories["Супы"],
            "dish_type": "food",
            "price": 380,
            "weight": 400,
            "ingredients": "Свекла, капуста, картофель, морковь, мясо, сметана",
            "is_available": True,
        },
        # Горячие блюда
        {
            "name": "Стейк Рибай",
            "description": "Сочный стейк из мраморной говядины с овощами гриль",
            "category": categories["Горячие блюда"],
            "dish_type": "food",
            "price": 1200,
            "weight": 350,
            "ingredients": "Говядина рибай, соль, перец, овощи гриль",
            "is_available": True,
        },
        {
            "name": "Лосось в соусе терияки",
            "description": "Филе лосося с соусом терияки и рисом",
            "category": categories["Горячие блюда"],
            "dish_type": "food",
            "price": 890,
            "weight": 300,
            "ingredients": "Лосось, соус терияки, рис, кунжут",
            "is_available": True,
        },
        # Гарниры
        {
            "name": "Картофель по-деревенски",
            "description": "Ароматный запеченный картофель с травами",
            "category": categories["Гарниры"],
            "dish_type": "food",
            "price": 220,
            "weight": 200,
            "ingredients": "Картофель, розмарин, чеснок, оливковое масло",
            "is_available": True,
        },
        {
            "name": "Овощи гриль",
            "description": "Сезонные овощи, приготовленные на гриле",
            "category": categories["Гарниры"],
            "dish_type": "food",
            "price": 280,
            "weight": 250,
            "ingredients": "Кабачки, баклажаны, перец, помидоры, оливковое масло",
            "is_available": True,
        },
        # Десерты
        {
            "name": "Тирамису",
            "description": "Классический итальянский десерт с кофе и маскарпоне",
            "category": categories["Десерты"],
            "dish_type": "food",
            "price": 380,
            "weight": 150,
            "ingredients": "Маскарпоне, савоярди, кофе, какао",
            "is_available": True,
        },
        {
            "name": "Чизкейк Нью-Йорк",
            "description": "Нежный чизкейк с ягодным соусом",
            "category": categories["Десерты"],
            "dish_type": "food",
            "price": 420,
            "weight": 180,
            "ingredients": "Сливочный сыр, песочное основание, ягодный соус",
            "is_available": True,
        },
        # Горячие напитки
        {
            "name": "Эспрессо",
            "description": "Классический крепкий кофе",
            "category": categories["Горячие напитки"],
            "dish_type": "drink",
            "price": 180,
            "volume": 30,
            "ingredients": "Кофе арабика",
            "is_available": True,
        },
        {
            "name": "Капучино",
            "description": "Кофе с нежной молочной пенкой",
            "category": categories["Горячие напитки"],
            "dish_type": "drink",
            "price": 240,
            "volume": 200,
            "ingredients": "Кофе, молоко",
            "is_available": True,
        },
        {
            "name": "Чай английский завтрак",
            "description": "Крепкий черный чай",
            "category": categories["Горячие напитки"],
            "dish_type": "drink",
            "price": 150,
            "volume": 300,
            "ingredients": "Черный чай",
            "is_available": True,
        },
        # Холодные напитки
        {
            "name": "Свежевыжатый апельсиновый сок",
            "description": "Натуральный сок из свежих апельсинов",
            "category": categories["Холодные напитки"],
            "dish_type": "drink",
            "price": 320,
            "volume": 250,
            "ingredients": "Апельсины",
            "is_available": True,
        },
        {
            "name": "Мохито безалкогольный",
            "description": "Освежающий напиток с лаймом и мятой",
            "category": categories["Холодные напитки"],
            "dish_type": "drink",
            "price": 280,
            "volume": 400,
            "ingredients": "Лайм, мята, содовая, сахар",
            "is_available": True,
        },
        # Алкогольные напитки
        {
            "name": "Пиво Heineken",
            "description": "Светлое лагер пиво",
            "category": categories["Алкогольные напитки"],
            "dish_type": "drink",
            "price": 280,
            "volume": 500,
            "ingredients": "Пиво",
            "is_available": True,
        },
        {
            "name": "Вино Merlot",
            "description": "Красное сухое вино, бокал",
            "category": categories["Алкогольные напитки"],
            "dish_type": "drink",
            "price": 450,
            "volume": 150,
            "ingredients": "Виноград Merlot",
            "is_available": True,
        },
        {
            "name": "Мохито классический",
            "description": "Классический коктейль с белым ромом",
            "category": categories["Алкогольные напитки"],
            "dish_type": "drink",
            "price": 520,
            "volume": 400,
            "ingredients": "Белый ром, лайм, мята, содовая, сахар",
            "is_available": True,
        },
    ]

    created_count = 0
    for item_data in menu_items_data:
        item, created = MenuItem.objects.get_or_create(
            name=item_data["name"], defaults=item_data
        )
        if created:
            created_count += 1
            print(f"Создано: {item.name} - {item.price} руб.")

    print(f"\n✅ Готово! Создано {created_count} позиций меню")

    # Статистика
    print("\n📊 Статистика меню:")
    for category in Category.objects.all().order_by("order"):
        count = MenuItem.objects.filter(category=category).count()
        print(f"  {category.name}: {count} позиций")


if __name__ == "__main__":
    create_sample_menu()
