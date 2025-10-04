from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, date, time
from tables.models import Table
from .models import Booking


def booking_view(request):
    """Отображает страницу бронирования с выбором даты и столиков."""
    selected_date = request.GET.get('date')

    # Если дата не указана, используем сегодняшнюю
    if selected_date:
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()

    # Получаем все активные столики
    tables = Table.objects.filter(is_active=True).order_by('number')

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
    for table in tables:
        available_slots = []
        for slot_value, slot_display in Booking.TIME_SLOTS:
            is_available = (table.id not in booked_slots or
                            slot_value not in booked_slots[table.id])

            # Проверяем, не прошел ли уже этот слот (для сегодняшней даты)
            if selected_date == date.today():
                is_available = is_available and slot_value > datetime.now().time()

            available_slots.append({
                'value': slot_value.strftime('%H:%M'),
                'display': slot_display,
                'is_available': is_available
            })

        tables_data.append({
            'table': table,
            'available_slots': available_slots
        })

    context = {
        'tables_data': tables_data,
        'selected_date': selected_date,
        'min_date': date.today(),
        'max_date': date.today().replace(year=date.today().year + 1),  # Можно бронировать на год вперед
    }
    return render(request, 'Bookings/bookings.html', context)


@login_required
def create_booking_view(request):
    """Обрабатывает создание бронирования через обычную форму."""
    if request.method == 'POST':
        try:
            table_id = request.POST.get('table_id')
            booking_date_str = request.POST.get('booking_date')
            time_slot_str = request.POST.get('time_slot')
            guests_count = request.POST.get('guests_count')
            special_requests = request.POST.get('special_requests', '')

            # Валидация данных
            if not all([table_id, booking_date_str, time_slot_str, guests_count]):
                messages.error(request, 'Все поля обязательны для заполнения.')
                return redirect('bookings:booking_view')

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

            # Проверка доступности временного слота
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
                time_slot=time_slot,
                guests_count=guests_count,
                special_requests=special_requests,
                status='pending'  # или 'confirmed' в зависимости от вашей логики
            )

            messages.success(request, f'Бронирование столика {table.number} на {booking_date} успешно создано!')
            return redirect('bookings:booking_view')

        except Table.DoesNotExist:
            messages.error(request, 'Столик не найден или неактивен.')
            return redirect('bookings:booking_view')
        except ValueError as e:
            messages.error(request, f'Неверный формат данных: {str(e)}')
            return redirect('bookings:booking_view')
        except Exception as e:
            messages.error(request, 'Произошла ошибка при создании бронирования.')
            return redirect('bookings:booking_view')

    # Если метод не POST, перенаправляем на страницу бронирования
    return redirect('bookings:booking_view')