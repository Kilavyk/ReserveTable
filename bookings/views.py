from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from datetime import datetime, date, time, timedelta
from tables.models import Table
from users.models import CustomUser
from .models import Booking


def booking_view(request):
    """Отображает страницу бронирования с выбором параметров и столиков."""
    # Если пользователь не авторизован, показываем сообщение
    if not request.user.is_authenticated:
        messages.info(request, 'Для бронирования столика необходимо авторизоваться.')

    # Получаем параметры из GET запроса или устанавливаем по умолчанию
    selected_date_str = request.GET.get('date')
    guests_count_str = request.GET.get('guests_count')
    time_slot_str = request.GET.get('time_slot')

    # Обработка выбранной даты
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()

    # Обработка количества гостей
    try:
        guests_count = int(guests_count_str) if guests_count_str else 2
    except ValueError:
        guests_count = 2

    # Обработка временного слота
    selected_time_slot = None
    selected_time_slot_display = ""
    if time_slot_str:
        try:
            # Преобразуем строку "HH:MM" в объект time
            selected_time_slot = datetime.strptime(time_slot_str, '%H:%M').time()
            # Найдем отображаемое имя для этого слота
            for slot_value, display_name in Booking.TIME_SLOTS:
                if slot_value == selected_time_slot:
                    selected_time_slot_display = display_name
                    break
        except ValueError:
            selected_time_slot = None
            selected_time_slot_display = ""

    # Если время не выбрано, устанавливаем ближайшее доступное
    if not selected_time_slot:
        now = datetime.now()
        current_time = now.time()
        current_date = now.date()
        # Если выбранная дата - сегодня, учитываем текущее время
        if selected_date == current_date:
            for slot_value, display_name in Booking.TIME_SLOTS:
                if slot_value > current_time:
                    selected_time_slot = slot_value
                    selected_time_slot_display = display_name
                    break
        else:
            # Если не сегодня, просто первый слот
            if Booking.TIME_SLOTS:
                selected_time_slot = Booking.TIME_SLOTS[0][0]
                selected_time_slot_display = Booking.TIME_SLOTS[0][1]

    # Получаем все активные столики, подходящие по вместимости
    suitable_tables = Table.objects.filter(
        is_active=True,
        max_guests__gte=guests_count
    ).order_by('max_guests', 'number')

    # Получаем бронирования на выбранную дату
    bookings_on_date = Booking.objects.filter(
        booking_date=selected_date,
        status__in=['confirmed', 'pending']
    ).select_related('table')

    # Создаем словарь занятых временных слотов для каждого столика
    booked_slots = {}
    for booking in bookings_on_date:
        if booking.table_id not in booked_slots:
            booked_slots[booking.table_id] = []
        booked_slots[booking.table_id].append(booking.time_slot)

    # Подготавливаем данные для шаблона
    tables_data = []
    available_tables_count = 0

    # Проверяем, что selected_time_slot не None перед использованием
    if selected_time_slot is not None:
        for table in suitable_tables:
            # Проверяем доступность выбранного слота для этого столика
            is_available = (table.id not in booked_slots or
                            selected_time_slot not in booked_slots[table.id])
            # Проверяем, не прошел ли уже этот слот (для сегодняшней даты)
            if selected_date == date.today():
                is_available = is_available and selected_time_slot > datetime.now().time()

            if is_available:
                available_tables_count += 1
                tables_data.append({
                    'table': {
                        'id': table.id,
                        'number': table.number,
                        'max_guests': table.max_guests,
                        'description': table.description if hasattr(table, 'description') else ''
                    },
                    'time_slot': selected_time_slot,
                    'time_slot_display': selected_time_slot_display,
                    'is_available': True
                })

    # Получаем список всех пользователей для выпадающего списка (только для администраторов)
    all_users = []
    if request.user.is_authenticated and request.user.groups.exists() or request.user.is_staff:
        all_users = CustomUser.objects.filter(is_active=True).order_by('first_name', 'last_name', 'email')

    context = {
        'tables_data': tables_data,
        'selected_date': selected_date,
        'guests_count': guests_count,
        'selected_time_slot': selected_time_slot,
        'selected_time_slot_display': selected_time_slot_display,
        'available_tables_count': available_tables_count,
        'time_slots': Booking.TIME_SLOTS,
        'today': date.today(),
        'all_users': all_users,  # Добавляем список пользователей в контекст
    }
    return render(request, 'bookings/bookings.html', context)


@login_required
def create_booking_view(request):
    """Обрабатывает создание бронирования."""
    if request.method == 'POST':
        try:
            table_id = request.POST.get('table_id')
            booking_date_str = request.POST.get('booking_date')
            time_slot_str = request.POST.get('time_slot')
            guests_count = request.POST.get('guests_count')
            special_requests = request.POST.get('special_requests', '')

            # Определяем пользователя для бронирования
            user_id = request.POST.get('user_id')
            if user_id and request.user.groups.exists():
                # Администратор может бронировать для других пользователей
                booking_user = get_object_or_404(CustomUser, id=user_id)
            else:
                # Обычный пользователь бронирует для себя
                booking_user = request.user

            # Преобразование данных
            booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
            time_slot = datetime.strptime(time_slot_str, '%H:%M').time()
            guests_count = int(guests_count)

            # Проверка даты
            if booking_date < date.today():
                messages.error(request, 'Нельзя забронировать столик на прошедшую дату.')
                return redirect('bookings:booking_view')

            if booking_date == date.today() and time_slot <= datetime.now().time():
                messages.error(request, 'Нельзя забронировать столик на прошедшее время.')
                return redirect('bookings:booking_view')

            # Проверка столика
            table = get_object_or_404(Table, pk=table_id, is_active=True)

            # Проверка вместимости
            if guests_count > table.max_guests:
                messages.error(request,
                               f'Количество гостей ({guests_count}) превышает максимальную вместимость столика ({table.max_guests}).')
                return redirect('bookings:booking_view')

            # Проверка доступности временного слота (теперь по переданному времени)
            existing_booking = Booking.objects.filter(
                table=table,
                booking_date=booking_date,
                time_slot=time_slot
            ).exclude(status='cancelled').exists()

            if existing_booking:
                messages.error(request, 'Этот столик уже забронирован на выбранное время.')
                return redirect('bookings:booking_view')

            # Создание бронирования
            booking = Booking.objects.create(
                user=booking_user,  # Используем определенного пользователя
                table=table,
                booking_date=booking_date,
                time_slot=time_slot,
                guests_count=guests_count,
                special_requests=special_requests,
                status='pending'
            )

            # Отправка email с подтверждением
            email_results = send_booking_confirmation_email(booking)

            # Используем get_time_slot_display для получения полного отображения времени
            time_display = booking.get_time_slot_display()
            # Форматируем дату
            formatted_date = booking_date.strftime('%d.%m.%y')

            # Формируем сообщение в нужном формате
            if booking_user == request.user:
                messages.success(request,
                                 f'Бронь столика №{table.number} подтверждена: {formatted_date}, {time_display}, {guests_count} гостя.')
            else:
                messages.success(request,
                                 f'Бронь столика №{table.number} для {booking_user.email} подтверждена: {formatted_date}, {time_display}, {guests_count} гостя.')

            if email_results['user']:
                messages.info(request, 'Письмо с деталями бронирования отправлено на почту.')
            else:
                messages.warning(request, 'Бронирование создано, но не удалось отправить письмо с подтверждением.')

            return redirect('bookings:booking_view')

        except Table.DoesNotExist:
            messages.error(request, 'Столик не найден или неактивен.')
            return redirect('bookings:booking_view')
        except ValueError as e:
            messages.error(request, f'Неверный формат данных: {str(e)}')
            return redirect('bookings:booking_view')
        except Exception as e:
            messages.error(request, f'Произошла ошибка при создании бронирования: {str(e)}')
            return redirect('bookings:booking_view')

    return redirect('bookings:booking_view')


def send_booking_confirmation_email(booking):
    """Отправляет email с подтверждением бронирования пользователю и уведомление администрации"""

    # Форматируем дату
    formatted_date = booking.booking_date.strftime('%d.%m.%Y')

    # Получаем отображаемое время
    time_display = booking.get_time_slot_display()

    # Безопасно получаем данные пользователя
    user = booking.user
    user_first_name = getattr(user, 'first_name', '')
    user_email = getattr(user, 'email', '')
    user_phone = getattr(user, 'phone_number', 'не указан')

    # Получаем домен для формирования полных ссылок
    domain = settings.DOMAIN

    # Формируем полный URL для страницы бронирования
    booking_detail_url = f"{domain}/bookings/booking/{booking.id}/"

    # Отправка подтверждения пользователю
    user_context = {
        'user_first_name': user_first_name,
        'user_email': user_email,
        'table_number': booking.table.number,
        'formatted_date': formatted_date,
        'time_display': time_display,
        'guests_count': booking.guests_count,
        'special_requests': booking.special_requests or '',
    }

    # Создаем HTML-сообщение для пользователя
    user_html_message = render_to_string('bookings/booking_confirmation_email.html', user_context)
    user_plain_message = strip_tags(user_html_message)

    user_subject = f'Бронирование столика №{booking.table.number} - Gourmet Haven'

    # Отправка уведомления администрации
    admin_context = {
        'booking_id': booking.id,
        'user_first_name': user_first_name,
        'user_last_name': getattr(user, 'last_name', 'не указано'),
        'user_email': user_email,
        'user_phone': user_phone,
        'table_number': booking.table.number,
        'table_description': booking.table.description if hasattr(booking.table, 'description') else 'не указано',
        'formatted_date': formatted_date,
        'time_display': time_display,
        'guests_count': booking.guests_count,
        'special_requests': booking.special_requests or 'не указаны',
        'booking_status': booking.get_status_display(),
        'created_at': booking.created_at.strftime('%d.%m.%Y %H:%M'),
        'domain': domain,
        'booking_detail_url': booking_detail_url,
    }

    admin_html_message = render_to_string('bookings/booking_notification_admin.html', admin_context)
    admin_plain_message = strip_tags(admin_html_message)

    admin_subject = f'Новое бронирование столика №{booking.table.number} - Gourmet Haven'

    email_results = {
        'user': False,
        'admin': False
    }

    try:
        # Отправка пользователю
        send_mail(
            subject=user_subject,
            message=user_plain_message,
            from_email=None,
            recipient_list=[user_email],
            html_message=user_html_message,
            fail_silently=False,
        )
        email_results['user'] = True
    except Exception as e:
        print(f"Ошибка отправки email пользователю: {str(e)}")

    try:
        # Отправка администрации
        admin_email = settings.EMAIL_HOST_USER  # Берем email администрации из настроек
        send_mail(
            subject=admin_subject,
            message=admin_plain_message,
            from_email=None,
            recipient_list=[admin_email],
            html_message=admin_html_message,
            fail_silently=False,
        )
        email_results['admin'] = True
    except Exception as e:
        print(f"Ошибка отправки email администрации: {str(e)}")

    return email_results


@login_required
@permission_required('bookings.view_booking', raise_exception=True)
def admin_panel_view(request):
    """Панель администратора для управления бронированиями"""

    # Получаем выбранную дату из GET параметра или используем сегодняшнюю
    selected_date_str = request.GET.get('date')
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()

    # Получаем все активные столики
    tables = Table.objects.filter(is_active=True).order_by('number')

    # Получаем все бронирования на выбранную дату
    bookings_on_date = Booking.objects.filter(
        booking_date=selected_date,
        status__in=['confirmed', 'pending']
    ).select_related('table', 'user')

    # Создаем словарь занятых временных слотов для каждого столика
    booked_slots = {}
    for booking in bookings_on_date:
        if booking.table_id not in booked_slots:
            booked_slots[booking.table_id] = []
        booked_slots[booking.table_id].append({
            'time_slot': booking.time_slot,
            'status': booking.status,
            'booking_id': booking.id
        })

    # Получаем текущее время для проверки прошедших слотов
    now = datetime.now()
    current_time = now.time()
    current_date = now.date()

    # Подготавливаем данные для шаблона
    tables_data = []
    for table in tables:
        table_slots = []

        # Для каждого временного слота проверяем доступность
        for slot_value, slot_display in Booking.TIME_SLOTS:
            # Проверяем, занят ли слот и его статус
            is_booked = False
            booking_status = None
            booking_id = None
            if table.id in booked_slots:
                for booking in booked_slots[table.id]:
                    if booking['time_slot'] == slot_value:
                        is_booked = True
                        booking_status = booking['status']
                        booking_id = booking['booking_id']
                        break

            # Проверяем, не прошел ли уже этот слот
            is_past = False
            if selected_date < current_date:
                is_past = True  # Прошедшая дата
            elif selected_date == current_date and slot_value <= current_time:
                is_past = True  # Сегодня, но время уже прошло

            # Определяем тип слота
            slot_type = 'available'
            if is_past:
                if is_booked:
                    if booking_status == 'pending':
                        slot_type = 'past_pending'  # Прошедшее и ожидает подтверждения
                    else:
                        slot_type = 'past_booked'  # Прошедшее и забронированное
                else:
                    slot_type = 'past_free'  # Прошедшее и свободное
            elif is_booked:
                if booking_status == 'pending':
                    slot_type = 'pending'  # Будущее и ожидает подтверждения
                else:
                    slot_type = 'booked'  # Будущее и забронированное

            table_slots.append({
                'time': slot_value,
                'display': slot_display,
                'is_available': not is_booked and not is_past,
                'is_booked': is_booked,
                'is_past': is_past,
                'slot_type': slot_type,
                'booking_status': booking_status,
                'booking_id': booking_id,
            })

        tables_data.append({
            'table': table,
            'slots': table_slots
        })

    context = {
        'tables_data': tables_data,
        'selected_date': selected_date,
        'today': date.today(),
        'now': now,
        'bookings_on_date': bookings_on_date,
    }

    return render(request, 'bookings/admin_panel.html', context)


@login_required
@permission_required('bookings.view_booking', raise_exception=True)
def booking_detail_view(request, booking_id):
    """Детальная страница бронирования с возможностью подтверждения/отмены"""
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'confirm' and booking.status != 'confirmed':
            booking.status = 'confirmed'
            booking.save()
            messages.success(request, f'Бронирование #{booking.id} подтверждено!')

        elif action == 'cancel' and booking.status != 'cancelled':
            booking.status = 'cancelled'
            booking.save()
            messages.success(request, f'Бронирование #{booking.id} отменено!')

        return redirect('bookings:booking_detail', booking_id=booking.id)

    context = {
        'booking': booking,
        'can_confirm': booking.status != 'confirmed' and not booking.is_past(),
        'can_cancel': booking.status != 'cancelled' and not booking.is_past(),
    }

    return render(request, 'bookings/booking_detail.html', context)


@login_required
def edit_booking_view(request, booking_id):
    """Редактирование существующего бронирования"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Проверяем, можно ли редактировать бронирование
    if booking.status == 'confirmed':
        messages.error(request, 'Нельзя изменить подтвержденное бронирование.',
                       extra_tags=f'booking_edit_{booking_id}')
        return redirect('users:profile')

    if booking.status == 'cancelled':
        messages.error(request, 'Нельзя изменить отмененное бронирование.',
                       extra_tags=f'booking_edit_{booking_id}')
        return redirect('users:profile')

    if booking.is_past():
        messages.error(request, 'Нельзя изменить прошедшее бронирование.',
                       extra_tags=f'booking_edit_{booking_id}')
        return redirect('users:profile')

    if request.method == 'POST':
        try:
            table_id = request.POST.get('table_id')
            booking_date_str = request.POST.get('booking_date')
            time_slot_str = request.POST.get('time_slot')
            guests_count = request.POST.get('guests_count')
            special_requests = request.POST.get('special_requests', '')

            # Преобразование данных
            booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
            time_slot = datetime.strptime(time_slot_str, '%H:%M').time()
            guests_count = int(guests_count)

            # Проверка даты
            if booking_date < date.today():
                messages.error(request, 'Нельзя забронировать столик на прошедшую дату.',
                               extra_tags=f'booking_edit_{booking_id}')
                return redirect('users:profile')

            if booking_date == date.today() and time_slot <= datetime.now().time():
                messages.error(request, 'Нельзя забронировать столик на прошедшее время.',
                               extra_tags=f'booking_edit_{booking_id}')
                return redirect('users:profile')

            # Проверка столика
            table = get_object_or_404(Table, pk=table_id, is_active=True)

            # Проверка вместимости
            if guests_count > table.max_guests:
                messages.error(request,
                               f'Количество гостей ({guests_count}) превышает максимальную вместимость столика ({table.max_guests}).',
                               extra_tags=f'booking_edit_{booking_id}')
                return redirect('users:profile')

            # Проверка доступности временного слота (исключая текущее бронирование)
            existing_booking = Booking.objects.filter(
                table=table,
                booking_date=booking_date,
                time_slot=time_slot
            ).exclude(id=booking_id).exclude(status='cancelled').exists()

            if existing_booking:
                messages.error(request, 'Этот столик уже забронирован на выбранное время.',
                               extra_tags=f'booking_edit_{booking_id}')
                return redirect('users:profile')

            # Обновление бронирования
            booking.table = table
            booking.booking_date = booking_date
            booking.time_slot = time_slot
            booking.guests_count = guests_count
            booking.special_requests = special_requests
            booking.save()

            messages.success(request, f'Бронирование столика №{table.number} успешно изменено!')
            return redirect('users:profile')

        except Exception as e:
            messages.error(request, f'Произошла ошибка при изменении бронирования: {str(e)}',
                           extra_tags=f'booking_edit_{booking_id}')
            return redirect('users:profile')

    # GET запрос - перенаправляем на профиль
    return redirect('users:profile')


@login_required
def cancel_booking_view(request, booking_id):
    """Отмена бронирования пользователем"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Проверяем, можно ли отменить бронирование
    if booking.is_past():
        messages.error(request, 'Нельзя отменить прошедшее бронирование.')
        return redirect('users:profile')

    if booking.status == 'cancelled':
        messages.error(request, 'Бронирование уже отменено.')
        return redirect('users:profile')

    # Отменяем бронирование
    booking.status = 'cancelled'
    booking.save()

    messages.success(request, f'Бронирование столика №{booking.table.number} отменено.')
    return redirect('users:profile')
