from django.db import models


class SiteContent(models.Model):
    CONTENT_TYPES = [
        # Главная страница
        ("index_welcome_title", "Главная - заголовок"),
        ("index_welcome_text", "Главная - описание"),
        ("index_service_romantic", "Главная - романтический ужин"),
        ("index_service_banquets", "Главная - банкеты"),
        ("index_service_delivery", "Главная - доставка"),
        ("index_contacts_address", "Главная - адрес"),
        ("index_contacts_phone", "Главная - телефон"),
        ("index_contacts_email", "Главная - email"),
        ("index_contacts_hours", "Главная - режим работы"),
        # Страница "О нас"
        ("about_history_title", "О нас - заголовок истории"),
        ("about_history_content", "О нас - история"),
        ("about_mission_title", "О нас - заголовок миссии"),
        ("about_mission_content", "О нас - миссия"),
        ("about_team_chef", "О нас - шеф-повар"),
        ("about_team_manager", "О нас - менеджер"),
        ("about_team_sommelier", "О нас - сомелье"),
        # Страница "Контакты"
        ("contacts_address", "Контакты - адрес"),
        ("contacts_phone", "Контакты - телефон"),
        ("contacts_email", "Контакты - email"),
        ("contacts_hours", "Контакты - часы работы"),
        ("contacts_services_romantic", "Контакты - романтический ужин"),
        ("contacts_services_corporate", "Контакты - корпоративное"),
        ("contacts_atmosphere", "Контакты - атмосфера"),
        ("contacts_cuisine", "Контакты - авторская кухня"),
        ("contacts_chef", "Контакты - шеф-повар"),
        ("contacts_service", "Контакты - премиальное обслуживание"),
        ("contacts_welcome", "Контакты - приветствие"),
        # Футер
        ("footer_copyright", "Футер - копирайт"),
        ("footer_tagline", "Футер - слоган"),
    ]

    content_type = models.CharField(
        max_length=50, choices=CONTENT_TYPES, unique=True, verbose_name="Тип контента"
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Заголовок",
        help_text="Дополнительный заголовок",
    )
    content = models.TextField(verbose_name="Содержание")
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Контент сайта"
        verbose_name_plural = "Элементы контента сайта"
        ordering = ["content_type"]

    def __str__(self):
        return f"{self.get_content_type_display()}"
