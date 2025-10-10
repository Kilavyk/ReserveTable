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

from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from .models import CustomUser
from bookings.models import Booking


def custom_login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        next_url = request.POST.get('next', '')

        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, email=email, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, 'Вы успешно вошли в систему.')

                    if next_url:
                        return redirect(next_url)
                    return redirect('core:index')
                else:
                    if user.verification_token:
                        messages.error(
                            request,
                            'Ваш аккаунт временно заблокирован. Завершите восстановление пароля по ссылке из письма.',
                            extra_tags='password_reset error'
                        )
                    else:
                        messages.error(
                            request,
                            'Ваш аккаунт не активирован. Проверьте вашу почту для подтверждения email.'
                        )
            else:
                messages.error(request, 'Неверный email или пароль.')
        else:
            messages.error(request, 'Неверный email или пароль.')

        return redirect(request.META.get('HTTP_REFERER', 'core:index'))

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
            try:
                send_mail(
                    subject="Подтверждение регистрации",
                    message="",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    html_message=render_to_string(
                        "users/verification_email.html",
                        {
                            "user": user,
                            "domain": getattr(settings, 'DOMAIN', request.get_host()),
                            "token": token,
                        },
                    ),
                )
                messages.success(
                    request,
                    "Регистрация прошла успешно! Пожалуйста, проверьте вашу почту для подтверждения email."
                )
            except Exception as e:
                messages.error(
                    request,
                    "Регистрация прошла успешно, но не удалось отправить письмо подтверждения. "
                    "Свяжитесь с администрацией."
                )
                print(f"Ошибка отправки email: {e}")

            if next_url:
                return redirect(next_url)
            return redirect('core:index')
        else:
            # Передаем ошибки формы в сообщения
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")

            return redirect(request.META.get('HTTP_REFERER', 'core:index'))

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


@login_required
def profile_view(request):
    """Отображает страницу личного кабинета пользователя."""

    # Получаем все бронирования пользователя, отсортированные по дате создания (новые сверху)
    bookings_list = Booking.objects.filter(user=request.user).select_related('table').order_by('-created_at')

    # Пагинация - 5 бронирований на страницу
    paginator = Paginator(bookings_list, 5)
    page_number = request.GET.get('page')

    try:
        bookings = paginator.page(page_number)
    except PageNotAnInteger:
        # Если page не integer, показываем первую страницу
        bookings = paginator.page(1)
    except EmptyPage:
        # Если page вне диапазона, показываем последнюю страницу
        bookings = paginator.page(paginator.num_pages)

    # Статистика для сайдбара
    bookings_count = bookings_list.count()
    active_bookings_count = bookings_list.filter(status='confirmed').count()
    pending_bookings_count = bookings_list.filter(status='pending').count()

    context = {
        'bookings': bookings,
        'bookings_count': bookings_count,
        'active_bookings_count': active_bookings_count,
        'pending_bookings_count': pending_bookings_count,
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


def password_reset_request(request):
    """Обработка запроса на восстановление пароля"""
    if request.method == 'POST':
        email = request.POST.get('email', '').lower().strip()
        next_url = request.POST.get('next', '')

        try:
            user = CustomUser.objects.get(email=email)

            # Генерируем токен для сброса пароля и делаем аккаунт неактивным
            reset_token = secrets.token_hex(32)
            user.verification_token = reset_token
            user.is_active = False  # Делаем аккаунт неактивным до сброса пароля
            user.save()

            # Отправка email для сброса пароля
            try:
                send_mail(
                    subject="Восстановление пароля",
                    message="",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    html_message=render_to_string(
                        "users/password_reset_email.html",
                        {
                            "user": user,
                            "domain": getattr(settings, 'DOMAIN', request.get_host()),
                            "token": reset_token,
                        },
                    ),
                )
                messages.success(
                    request,
                    "Инструкции по восстановлению пароля отправлены на ваш email.",
                    extra_tags="password_reset success"
                )
            except Exception as e:
                # Если не удалось отправить email, возвращаем аккаунт в активное состояние
                user.is_active = True
                user.verification_token = None
                user.save()
                messages.error(
                    request,
                    "Не удалось отправить письмо с инструкциями. Попробуйте позже или свяжитесь с администрацией.",
                    extra_tags="password_reset error"
                )
                print(f"Ошибка отправки email: {e}")

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

@login_required
@permission_required('users.view_customuser', raise_exception=True)
def users_management_view(request):
    """Страница управления пользователями"""
    # Получаем всех пользователей, отсортированных по дате регистрации (новые сверху)
    users_list = CustomUser.objects.all().order_by('-date_joined')

    # Пагинация - 10 пользователей на страницу
    paginator = Paginator(users_list, 10)
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
            is_staff = request.POST.get('is_staff') == 'on'

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

            # Создаем пользователя
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                first_name=first_name if first_name else '',
                last_name=last_name if last_name else '',
                phone_number=phone_number if phone_number else '',
                is_active=is_active,
                is_staff=is_staff
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
            is_staff = request.POST.get('is_staff') == 'on'

            # Получаем пользователя
            user = get_object_or_404(CustomUser, id=user_id)

            # Валидация
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
            user.is_staff = is_staff

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