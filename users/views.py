from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import secrets

from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import CustomUser
from bookings.models import Booking


def _send_email(subject, template_name, context, recipient_list):
    """Вспомогательная функция для отправки email"""
    try:
        send_mail(
            subject=subject,
            message="",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipient_list,
            html_message=render_to_string(template_name, context),
        )
        return True
    except Exception as e:
        print(f"Ошибка отправки email: {e}")
        return False


def _handle_form_errors(form, request):
    """Обработка ошибок формы и добавление их в сообщения"""
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, f"{error}")


def _get_redirect_url(request, next_url_param='next'):
    """Получение URL для редиректа с учетом next параметра"""
    next_url = request.POST.get(next_url_param, '')
    if next_url:
        return next_url
    return request.META.get('HTTP_REFERER', 'core:index')


def _authenticate_and_login(request, email, password):
    """Аутентификация и вход пользователя"""
    user = authenticate(request, email=email, password=password)

    if user is not None and user.is_active:
        login(request, user)
        messages.success(request, 'Вы успешно вошли в систему.')
        return user
    return None


def custom_login_view(request):
    """Обрабатывает аутентификацию и вход пользователя в систему!"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        next_url = request.POST.get('next', '')

        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = _authenticate_and_login(request, email, password)
            if user:
                if next_url:
                    return redirect(next_url)
                return redirect('core:index')
            else:
                # Обработка неактивного пользователя
                try:
                    user = CustomUser.objects.get(email=email)
                    if user.verification_token:
                        messages.error(
                            request,
                            'Завершите восстановление пароля по ссылке из письма.',
                            extra_tags='password_reset error'
                        )
                    else:
                        messages.error(
                            request,
                            'Ваш аккаунт не активирован. Проверьте вашу почту для подтверждения email.'
                        )
                except CustomUser.DoesNotExist:
                    messages.error(request, 'Неверный email или пароль.')
        else:
            messages.error(request, 'Неверный email или пароль.')

        return redirect(_get_redirect_url(request))

    return redirect('core:index')


def custom_register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        next_url = request.POST.get('next', '')

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Пользователь не активен до верификации email
            token = user.generate_verification_token()
            user.save()

            # Отправка email для верификации
            email_sent = _send_email(
                subject="Подтверждение регистрации",
                template_name="users/verification_email.html",
                context={
                    "user": user,
                    "domain": getattr(settings, 'DOMAIN', request.get_host()),
                    "token": token,
                },
                recipient_list=[user.email]
            )

            if email_sent:
                messages.success(
                    request,
                    "Регистрация прошла успешно! Пожалуйста, проверьте вашу почту для подтверждения email."
                )
            else:
                messages.error(
                    request,
                    "Регистрация прошла успешно, но не удалось отправить письмо подтверждения. "
                    "Свяжитесь с администрацией."
                )

            if next_url:
                return redirect(next_url)
            return redirect('core:index')
        else:
            _handle_form_errors(form, request)
            return redirect(_get_redirect_url(request))

    return redirect('core:index')


def email_verification(request, token):
    """Верификация email пользователя"""
    user = get_object_or_404(CustomUser, verification_token=token)
    user.is_active = True
    user.verification_token = None  # Очищаем токен после использования
    user.save()

    # Автоматически авторизуем пользователя
    login(request, user)

    messages.success(
        request,
        "Ваш email успешно подтверждён! Теперь вы можете войти в систему."
    )
    return redirect('users:login')


def custom_logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('core:index')


def _get_user_bookings_stats(user):
    """Получение статистики бронирований пользователя"""
    bookings_list = Booking.objects.filter(user=user).select_related('table').order_by('-created_at')

    return {
        'bookings_list': bookings_list,
        'bookings_count': bookings_list.count(),
        'active_bookings_count': bookings_list.filter(status='confirmed').count(),
        'pending_bookings_count': bookings_list.filter(status='pending').count(),
    }


@login_required
def profile_view(request):
    """Отображает страницу личного кабинета пользователя."""
    stats = _get_user_bookings_stats(request.user)

    # Пагинация - 5 бронирований на страницу
    paginator = Paginator(stats['bookings_list'], 5)
    page_number = request.GET.get('page')

    try:
        bookings = paginator.page(page_number)
    except PageNotAnInteger:
        # Если page не integer, показываем первую страницу
        bookings = paginator.page(1)
    except EmptyPage:
        # Если page вне диапазона, показываем последнюю страницу
        bookings = paginator.page(paginator.num_pages)

    context = {
        'bookings': bookings,
        'bookings_count': stats['bookings_count'],
        'active_bookings_count': stats['active_bookings_count'],
        'pending_bookings_count': stats['pending_bookings_count'],
        'time_slots': Booking.TIME_SLOTS,
    }

    return render(request, 'users/profile.html', context)


@login_required
def profile_edit_view(request):
    """Обрабатывает редактирование профиля пользователя."""
    if request.method == 'POST':
        try:
            user = request.user

            # Обновляем текстовые поля
            user.first_name = request.POST.get('first_name', '').strip()
            user.last_name = request.POST.get('last_name', '').strip()
            user.phone_number = request.POST.get('phone_number', '').strip()

            # Обработка удаления фотографии
            delete_photo = request.POST.get('delete_photo') == 'true'
            if delete_photo and user.photo:
                user.photo.delete(save=False)
                user.photo = None

            # Обработка загрузки новой фотографии
            if 'photo' in request.FILES:
                photo_file = request.FILES['photo']

                # Удаляем старое фото если оно есть
                if user.photo:
                    user.photo.delete(save=False)

                # Сохраняем новое фото
                user.photo = photo_file

            user.save()
            messages.success(request, 'Профиль успешно обновлен!')

        except Exception as e:
            messages.error(
                request,
                f'Произошла ошибка при обновлении профиля: {str(e)}',
                extra_tags='profile'
            )

    return redirect('users:profile')


def _handle_password_reset_request(user, request):
    """Обработка запроса на сброс пароля для конкретного пользователя"""
    reset_token = secrets.token_hex(32)
    user.verification_token = reset_token
    user.is_active = False  # Делаем аккаунт неактивным до сброса пароля
    user.save()

    # Отправка email для сброса пароля
    email_sent = _send_email(
        subject="Восстановление пароля",
        template_name="users/password_reset_email.html",
        context={
            "user": user,
            "domain": getattr(settings, 'DOMAIN', request.get_host()),
            "token": reset_token,
        },
        recipient_list=[user.email]
    )

    if email_sent:
        messages.success(
            request,
            "Инструкции по восстановлению пароля отправлены на ваш email.",
            extra_tags="password_reset success"
        )
    else:
        # Если не удалось отправить email, возвращаем аккаунт в активное состояние
        user.is_active = True
        user.verification_token = None
        user.save()
        messages.error(
            request,
            "Не удалось отправить письмо с инструкциями. Попробуйте позже или свяжитесь с администрацией.",
            extra_tags="password_reset error"
        )

    return email_sent


def password_reset_request(request):
    """Обработка запроса на восстановление пароля"""
    if request.method == 'POST':
        email = request.POST.get('email', '').lower().strip()
        next_url = request.POST.get('next', '')

        try:
            user = CustomUser.objects.get(email=email)
            _handle_password_reset_request(user, request)

        except CustomUser.DoesNotExist:
            # Не сообщаем, что пользователь не найден (в целях безопасности)
            messages.success(
                request,
                "Если email зарегистрирован в системе, инструкции по восстановлению пароля будут отправлены на указанный адрес.",
                extra_tags="password_reset success"
            )

        if next_url:
            return redirect(next_url)
        return redirect('core:index')

    return redirect('core:index')


def password_reset_confirm(request, token):
    """Подтверждение сброса пароля и установка нового пароля"""
    try:
        user = CustomUser.objects.get(verification_token=token)
    except CustomUser.DoesNotExist:
        messages.error(
            request,
            "Недействительная или устаревшая ссылка для восстановления пароля.",
            extra_tags="password_reset error"
        )
        return redirect('core:index')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password and confirm_password:
            if new_password == confirm_password:
                if len(new_password) >= 8:  # Минимальная длина пароля
                    # Устанавливаем новый пароль и активируем аккаунт
                    user.set_password(new_password)
                    user.verification_token = None  # Очищаем токен после использования
                    user.is_active = True  # Активируем аккаунт
                    user.save()

                    # Автоматически авторизуем пользователя с новым паролем
                    user = authenticate(request, email=user.email, password=new_password)
                    if user is not None:
                        login(request, user)

                    messages.success(
                        request,
                        "Пароль успешно изменен!",
                        extra_tags="password_reset success"
                    )
                    # Перенаправляем на страницу бронирования
                    return redirect('bookings:booking_view')
                else:
                    messages.error(
                        request,
                        "Пароль должен содержать минимум 8 символов.",
                        extra_tags="password_reset error"
                    )
            else:
                messages.error(
                    request,
                    "Пароли не совпадают.",
                    extra_tags="password_reset error"
                )
        else:
            messages.error(
                request,
                "Все поля обязательны для заполнения.",
                extra_tags="password_reset error"
            )

    # Отображаем страницу с формой сброса пароля
    return render(request, 'users/password_reset_confirm.html', {
        'token': token,
        'user': user
    })


def _validate_user_fields(first_name, last_name, phone_number, request):
    """Валидация полей пользователя"""
    if len(first_name) > 30:
        messages.error(request, 'Имя не может быть длиннее 30 символов.')
        return False

    if len(last_name) > 30:
        messages.error(request, 'Фамилия не может быть длиннее 30 символов.')
        return False

    if len(phone_number) > 20:
        messages.error(request, 'Телефон не может быть длиннее 20 символов.')
        return False

    return True


@login_required
@permission_required('users.view_customuser', raise_exception=True)
def users_management_view(request):
    """Страница управления пользователями"""
    # Получаем всех пользователей, отсортированных по email (алфавитный порядок)
    users_list = CustomUser.objects.all().order_by('email')

    # Пагинация - 50 пользователей на страницу
    paginator = Paginator(users_list, 50)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)

    context = {
        'users': users,
    }
    return render(request, 'users/users_management.html', context)


@login_required
@permission_required('users.add_customuser', raise_exception=True)
def add_user_view(request):
    """Добавление нового пользователя"""
    if request.method == 'POST':
        try:
            email = request.POST.get('email', '').strip().lower()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            phone_number = request.POST.get('phone_number', '').strip()
            password = request.POST.get('password', '')
            is_active = request.POST.get('is_active') == 'on'

            # Валидация
            if not email:
                messages.error(request, 'Email обязателен для заполнения.')
                return redirect('users:users_management')

            if not password:
                messages.error(request, 'Пароль обязателен для заполнения.')
                return redirect('users:users_management')

            if len(password) < 8:
                messages.error(request, 'Пароль должен содержать минимум 8 символов.')
                return redirect('users:users_management')

            # Валидация длины полей
            if not _validate_user_fields(first_name, last_name, phone_number, request):
                return redirect('users:users_management')

            # Создаем пользователя
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                first_name=first_name if first_name else '',
                last_name=last_name if last_name else '',
                phone_number=phone_number if phone_number else '',
                is_active=is_active,
                is_staff=False
            )

            messages.success(request, f'Пользователь {user.email} успешно добавлен!')

        except IntegrityError:
            messages.error(request, f'Пользователь с email {email} уже существует.')
        except Exception as e:
            messages.error(request, f'Произошла ошибка при добавлении пользователя: {str(e)}')

    return redirect('users:users_management')


@login_required
@permission_required('users.change_customuser', raise_exception=True)
def edit_user_view(request):
    """Редактирование пользователя"""
    if request.method == 'POST':
        try:
            user_id = request.POST.get('user_id')
            email = request.POST.get('email', '').strip().lower()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            phone_number = request.POST.get('phone_number', '').strip()
            password = request.POST.get('password', '')
            is_active = request.POST.get('is_active') == 'on'

            # Получаем пользователя
            user = get_object_or_404(CustomUser, id=user_id)

            # Защита от редактирования администраторов
            if user.is_superuser:
                messages.error(request, 'Нельзя редактировать администратора через интерфейс.')
                return redirect('users:users_management')

            # Валидация длины полей
            if not _validate_user_fields(first_name, last_name, phone_number, request):
                return redirect('users:users_management')

            # Валидация email
            if not email:
                messages.error(request, 'Email обязателен для заполнения.')
                return redirect('users:users_management')

            # Проверяем, не занят ли email другим пользователем
            if CustomUser.objects.filter(email=email).exclude(id=user_id).exists():
                messages.error(request, f'Пользователь с email {email} уже существует.')
                return redirect('users:users_management')

            # Обновляем пользователя
            user.email = email
            user.first_name = first_name if first_name else ''
            user.last_name = last_name if last_name else ''
            user.phone_number = phone_number if phone_number else ''
            user.is_active = is_active

            # Обновляем пароль, если он указан
            if password:
                if len(password) < 8:
                    messages.error(request, 'Пароль должен содержать минимум 8 символов.')
                    return redirect('users:users_management')
                user.set_password(password)

            user.save()

            messages.success(request, f'Пользователь {user.email} успешно обновлен!')

        except CustomUser.DoesNotExist:
            messages.error(request, 'Пользователь не найден.')
        except Exception as e:
            messages.error(request, f'Произошла ошибка при обновлении пользователя: {str(e)}')

    return redirect('users:users_management')


@login_required
@permission_required('users.delete_customuser', raise_exception=True)
def delete_user_view(request):
    """Удаление пользователя"""
    if request.method == 'POST':
        try:
            user_id = request.POST.get('user_id')
            user = get_object_or_404(CustomUser, id=user_id)
            user_email = user.email

            # Нельзя удалить самого себя
            if user == request.user:
                messages.error(request, 'Вы не можете удалить свой собственный аккаунт.')
                return redirect('users:users_management')

            # Удаляем пользователя
            user.delete()

            messages.success(request, f'Пользователь {user_email} успешно удален!')

        except CustomUser.DoesNotExist:
            messages.error(request, 'Пользователь не найден.')
        except Exception as e:
            messages.error(request, f'Произошла ошибка при удалении пользователя: {str(e)}')

    return redirect('users:users_management')
