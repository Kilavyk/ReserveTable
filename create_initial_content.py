# python create_initial_content.py

import os
import sys

import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django.setup()

from core.models import SiteContent  # noqa: E402


def create_initial_content():
    """Создает начальный контент для сайта на основе текста из шаблонов"""

    initial_content = [
        # Главная страница
        {
            "content_type": "index_welcome_title",
            "title": "Добро пожаловать в Gourmet Haven",
            "content": "Добро пожаловать в Gourmet Haven",
        },
        {
            "content_type": "index_welcome_text",
            "title": "",
            "content": (
                "Наш ресторан — это место, где изысканная кухня встречается с "
                "уютной атмосферой и безупречным сервисом. Мы используем только "
                "свежайшие ингредиенты и создаём блюда, вдохновлённые мировыми "
                "кулинарными традициями."
            ),
        },
        {
            "content_type": "index_service_romantic",
            "title": "",
            "content": "Идеальное место для особенных моментов с любимым человеком.",
        },
        {
            "content_type": "index_service_banquets",
            "title": "",
            "content": "Организуем свадьбы, юбилеи и корпоративы любого масштаба.",
        },
        {
            "content_type": "index_service_delivery",
            "title": "",
            "content": "Наслаждайтесь ресторанной кухней у себя дома.",
        },
        {
            "content_type": "index_contacts_address",
            "title": "",
            "content": "г. Москва, ул. Вкусная, д. 42",
        },
        {
            "content_type": "index_contacts_phone",
            "title": "",
            "content": "+7 (495) 123-45-67",
        },
        {
            "content_type": "index_contacts_email",
            "title": "",
            "content": "info@gourmethaven.ru",
        },
        {
            "content_type": "index_contacts_hours",
            "title": "",
            "content": "ежедневно с 12:00 до 00:00",
        },
        # Страница "О нас"
        {
            "content_type": "about_history_title",
            "title": "История ресторана",
            "content": "История ресторана",
        },
        {
            "content_type": "about_history_content",
            "title": "",
            "content": (
                "В 2024 году один мечтатель решил, что пора наконец-то выучить "
                "Python. Его первое приложение — скромное приложение которое "
                "хранит русские и английские слова и предлагает пользователю "
                "их угадывать."
            ),
        },
        {
            "content_type": "about_history_content_extra",
            "title": "",
            "content": (
                'От "Hello World" до "Hello Gourmet Haven" — так небольшой '
                "словарный тренажер превратился в целый ресторанный сайт."
            ),
        },
        {
            "content_type": "about_mission_title",
            "title": "Миссия и ценности",
            "content": "Миссия и ценности",
        },
        {
            "content_type": "about_mission_content",
            "title": "",
            "content": (
                "Наша миссия — создавать незабываемые гастрономические "
                "впечатления, используя только лучшие ингредиенты и "
                "инновационные подходы."
            ),
        },
        {
            "content_type": "about_quality",
            "title": "",
            "content": "Мы используем только свежие и качественные продукты.",
        },
        {
            "content_type": "about_hospitality",
            "title": "",
            "content": "Каждый гость — как дома.",
        },
        {
            "content_type": "about_innovation",
            "title": "",
            "content": "Современные технологии в традиционной кухне.",
        },
        {
            "content_type": "about_sustainability",
            "title": "",
            "content": "Мы заботимся о природе и обществе.",
        },
        {
            "content_type": "about_team_chef",
            "title": "Шеф-повар Алексей Петров",
            "content": "Шеф-повар Алексей Петров",
        },
        {
            "content_type": "about_team_chef_desc",
            "title": "",
            "content": "Обладатель множества наград, специалист по международной кухне.",
        },
        {
            "content_type": "about_team_manager",
            "title": "Менеджер по обслуживанию Мария Соколова",
            "content": "Менеджер по обслуживанию Мария Соколова",
        },
        {
            "content_type": "about_team_manager_desc",
            "title": "",
            "content": "Отвечает за безупречный сервис и комфорт наших гостей.",
        },
        {
            "content_type": "about_team_sommelier",
            "title": "Сомелье Иван Козлов",
            "content": "Сомелье Иван Козлов",
        },
        {
            "content_type": "about_team_sommelier_desc",
            "title": "",
            "content": "Эксперт по винам, подберёт идеальное сочетание к вашему блюду.",
        },
        # Страница "Контакты"
        {
            "content_type": "contacts_welcome",
            "title": "Свяжитесь с нами",
            "content": "Свяжитесь с нами",
        },
        {
            "content_type": "contacts_address",
            "title": "",
            "content": "г. Москва, ул. Вкусная, д. 42",
        },
        {
            "content_type": "contacts_phone",
            "title": "",
            "content": "+7 (495) 123-45-67",
        },
        {
            "content_type": "contacts_email",
            "title": "",
            "content": "info@gourmethaven.ru",
        },
        {
            "content_type": "contacts_hours",
            "title": "",
            "content": "12:00 - 00:00"
        },
        {
            "content_type": "contacts_services_romantic",
            "title": "",
            "content": "Романтический ужин",
        },
        {
            "content_type": "contacts_services_corporate",
            "title": "",
            "content": "Корпоративное обслуживание",
        },
        {
            "content_type": "contacts_atmosphere",
            "title": "",
            "content": "Уютная атмосфера",
        },
        {
            "content_type": "contacts_cuisine",
            "title": "",
            "content": "Авторская кухня"
        },
        {
            "content_type": "contacts_chef",
            "title": "",
            "content": "Шеф-повар с мишленовским опытом",
        },
        {
            "content_type": "contacts_service",
            "title": "",
            "content": "Премиальное обслуживание",
        },
        # Футер
        {
            "content_type": "footer_copyright",
            "title": "",
            "content": "© 2025 Gourmet Haven. Все права защищены.",
        },
        {
            "content_type": "footer_tagline",
            "title": "",
            "content": "Создано с любовью к гастрономии.",
        },
    ]

    created_count = 0
    updated_count = 0

    for item in initial_content:
        content_type = item["content_type"]
        title = item["title"]
        content = item["content"]

        # Пытаемся найти существующую запись
        try:
            site_content = SiteContent.objects.get(content_type=content_type)
            # Если запись существует, обновляем её
            if site_content.title != title or site_content.content != content:
                site_content.title = title
                site_content.content = content
                site_content.save()
                updated_count += 1
                print(f"✓ Обновлено: {content_type}")
            else:
                print(f"○ Без изменений: {content_type}")

        except SiteContent.DoesNotExist:
            # Если записи нет, создаём новую
            SiteContent.objects.create(
                content_type=content_type,
                title=title,
                content=content,
                is_active=True
            )
            created_count += 1
            print(f"✓ Создано: {content_type}")

    print("\n=== Результат ===")
    print(f"Создано записей: {created_count}")
    print(f"Обновлено записей: {updated_count}")
    print(f"Всего обработано: {created_count + updated_count}")


if __name__ == "__main__":
    print("Запуск наполнения базы данных начальным контентом...")
    create_initial_content()
    print("\nГотово! Проверьте контент в админке: /admin/core/sitecontent/")
