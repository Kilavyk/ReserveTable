from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.db import IntegrityError
from .models import CustomUser


def custom_login_view(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        next_url = request.POST.get('next', '')

        user = authenticate(request, phone_number=phone_number, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Вы успешно вошли в систему.')

            # Перенаправляем на next URL или на главную
            if next_url:
                return redirect(next_url)
            return redirect('core:index')
        else:
            messages.error(request, 'Неверный номер телефона или пароль.')
            # Возвращаем на ту же страницу с открытым модальным окном авторизации
            return redirect(request.META.get('HTTP_REFERER', 'core:index'))

    return redirect('core:index')


def custom_register_view(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        next_url = request.POST.get('next', '')

        # Валидация данных
        if not phone_number or not password:
            messages.error(request, 'Номер телефона и пароль обязательны для заполнения.')
            return redirect(request.META.get('HTTP_REFERER', 'core:index'))

        if password != password_confirm:
            messages.error(request, 'Пароли не совпадают.')
            return redirect(request.META.get('HTTP_REFERER', 'core:index'))

        if len(password) < 6:
            messages.error(request, 'Пароль должен содержать не менее 6 символов.')
            return redirect(request.META.get('HTTP_REFERER', 'core:index'))

        # Создание пользователя
        try:
            user = CustomUser.objects.create_user(
                phone_number=phone_number,
                password=password
            )
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')

            # Перенаправляем на next URL или на главную
            if next_url:
                return redirect(next_url)
            return redirect('core:index')

        except IntegrityError:
            messages.error(request, 'Данный номер телефона уже зарегистрирован.')
            return redirect(request.META.get('HTTP_REFERER', 'core:index'))
        except Exception as e:
            messages.error(request, 'Произошла ошибка при регистрации. Пожалуйста, попробуйте еще раз.')
            print(f"Ошибка регистрации: {e}")
            return redirect(request.META.get('HTTP_REFERER', 'core:index'))

    return redirect('core:index')


def custom_logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('core:index')


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from bookings.models import Booking


@login_required
def profile_view(request):
    """Отображает страницу личного кабинета пользователя."""
    # Получаем все бронирования пользователя, отсортированные по дате создания (новые сверху)
    bookings = Booking.objects.filter(user=request.user).select_related('table').order_by('-created_at')

    # Статистика для сайдбара
    bookings_count = bookings.count()
    active_bookings_count = bookings.filter(status='confirmed').count()
    pending_bookings_count = bookings.filter(status='pending').count()

    context = {
        'bookings': bookings,
        'bookings_count': bookings_count,
        'active_bookings_count': active_bookings_count,
        'pending_bookings_count': pending_bookings_count,
    }

    return render(request, 'users/profile.html', context)


@login_required
def profile_edit_view(request):
    """Обрабатывает редактирование профиля пользователя."""
    if request.method == 'POST':
        try:
            user = request.user
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            delete_photo = request.POST.get('delete_photo') == 'true'

            # Обновляем данные пользователя
            user.first_name = first_name
            user.last_name = last_name

            # Обработка удаления фотографии
            if delete_photo and user.photo:
                user.photo.delete(save=False)
                user.photo = None

            # Обработка загрузки новой фотографии - исправлено имя поля
            elif 'new_photo' in request.FILES:
                photo_file = request.FILES['new_photo']
                # Проверяем размер файла (максимум 5MB)
                if photo_file.size > 5 * 1024 * 1024:
                    messages.error(request, 'Размер файла не должен превышать 5MB.', extra_tags='profile')
                    return redirect('users:profile')

                # Проверяем тип файла
                allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
                if photo_file.content_type not in allowed_types:
                    messages.error(request, 'Допустимы только файлы изображений (JPEG, PNG, GIF, WebP).',
                                   extra_tags='profile')
                    return redirect('users:profile')

                # Удаляем старое фото если оно есть
                if user.photo:
                    user.photo.delete(save=False)

                user.photo = photo_file

            user.save()
            messages.success(request, 'Профиль успешно обновлен!')

        except Exception as e:
            messages.error(request, f'Произошла ошибка при обновлении профиля: {str(e)}', extra_tags='profile')

    return redirect('users:profile')