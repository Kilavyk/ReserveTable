from django import template

from core.models import SiteContent

register = template.Library()


@register.simple_tag
def get_content(content_type, default_text=""):
    """
    Получает контент по типу. Если не найден - возвращает текст по умолчанию
    """
    try:
        content = SiteContent.objects.get(content_type=content_type, is_active=True)
        return content.content
    except SiteContent.DoesNotExist:
        return default_text


@register.simple_tag
def get_content_title(content_type, default_title=""):
    """
    Получает заголовок по типу. Если не найден - возвращает заголовок по умолчанию
    """
    try:
        content = SiteContent.objects.get(content_type=content_type, is_active=True)
        return content.title if content.title else default_title
    except SiteContent.DoesNotExist:
        return default_title
