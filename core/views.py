import re

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils import timezone


def index(request):
    return render(request, "core/index.html")


def about(request):
    return render(request, "core/about.html")


def contacts(request):
    return render(request, "core/contacts.html")


def is_valid_email(email):
    """Проверка валидности email"""
    if not email:
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def feedback(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        message = request.POST.get("message", "").strip()
        timestamp = timezone.now().strftime("%d.%m.%Y в %H:%M")

        # Проверяем, что хотя бы одно поле заполнено
        if not any([name, email, phone, message]):
            messages.warning(request, "Пожалуйста, заполните хотя бы одно поле формы.")
            return redirect("core:index")

        try:
            # Контекст для шаблонов
            context = {
                "name": name or "Не указано",
                "email": email or "Не указан",
                "phone": phone or "Не указан",
                "message": message or "Не указано",
                "timestamp": timestamp,
            }

            # 1. Письмо владельцам сайта (HTML)
            owner_subject = "Новое сообщение обратной связи"
            if name:
                owner_subject += f" от {name}"

            owner_message_html = render_to_string(
                "core/emails/feedback_to_owner.html", context
            )

            # Отправка письма владельцам
            send_mail(
                owner_subject,
                "Пожалуйста, включите поддержку HTML для просмотра этого письма.",
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER],
                html_message=owner_message_html,
                fail_silently=False,
            )

            # 2. Письмо пользователю (только если указан валидный email)
            if email and is_valid_email(email):
                user_subject = "Благодарим за обратную связь!"
                user_message_html = render_to_string(
                    "core/emails/feedback_to_user.html", context
                )

                # Отправка письма пользователю
                send_mail(
                    user_subject,
                    "Пожалуйста, включите поддержку HTML для просмотра этого письма.",
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    html_message=user_message_html,
                    fail_silently=False,
                )

                messages.success(
                    request,
                    "Ваше сообщение успешно отправлено! Мы свяжемся с вами при необходимости.",
                )
            else:
                messages.success(
                    request,
                    "Ваше сообщение успешно отправлено! Спасибо за обратную связь.",
                )

        except Exception as e:
            messages.error(
                request,
                "Произошла ошибка при отправке сообщения. Пожалуйста, попробуйте позже.",
            )
            # Логируем ошибку для отладки
            print(f"Ошибка отправки сообщения: {e}")

        return redirect("core:index")

    return redirect("core:index")
