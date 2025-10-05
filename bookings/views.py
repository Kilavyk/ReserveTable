from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime, date, time, timedelta
from tables.models import Table
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

    context = {
        'tables_data': tables_data,
        'selected_date': selected_date,
        'guests_count': guests_count,
        'selected_time_slot': selected_time_slot,
        'selected_time_slot_display': selected_time_slot_display,
        'available_tables_count': available_tables_count,
        'time_slots': Booking.TIME_SLOTS,
        'today': date.today(),
    }
    return render(request, 'Bookings/bookings.html', context)


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
                time_slot=time_slot,
                status__in=['confirmed', 'pending']
            ).exists()
            if existing_booking:
                messages.error(request, 'Этот столик уже забронирован на выбранное время.')
                return redirect('bookings:booking_view')

            # Создание бронирования
            booking = Booking.objects.create(
                user=request.user,
                table=table,
                booking_date=booking_date,
                time_slot=time_slot, # Сохраняем переданное время
                guests_count=guests_count,
                special_requests=special_requests,
                status='pending'
            )
            # Используем get_time_slot_display для получения полного отображения времени
            time_display = booking.get_time_slot_display()
            # Форматируем дату
            formatted_date = booking_date.strftime('%d.%m.%y')
            # Формируем сообщение в нужном формате
            messages.success(request, f'Бронь столика №{table.number} подтверждена: {formatted_date}, {time_display}, {guests_count} гостя.')
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
