# Bookings/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from tables.models import Table
from .models import Booking
from users.models import CustomUser # Импортируем кастомного пользователя
import json
from datetime import datetime, date, time

def booking_view(request):
    """Отображает страницу бронирования."""
    # Получаем все столики
    tables = Table.objects.filter(is_active=True).order_by('number')

    # Получаем бронирования на сегодня (или на нужную дату, можно сделать фильтр)
    # Для упрощения, пока возьмем все активные бронирования на сегодня
    # Или все бронирования с подтвержденным статусом
    # Выберем все подтвержденные и ожидающие бронирования
    # Важно: чтобы проверять занятость на *конкретную дату*, нужно передавать дату из формы или использовать сегодняшнюю
    # Пока используем сегодняшнюю дату
    today = date.today()
    active_bookings = Booking.objects.filter(
        status__in=['confirmed', 'pending'],
        booking_date=today
    ).select_related('table')

    # Создаем словарь, где ключ - id столика, значение - True (занят) или False (свободен)
    booked_table_ids = {booking.table_id for booking in active_bookings}

    # Добавляем атрибут is_booked к каждому объекту Table
    tables_with_status = []
    for table in tables:
        table.is_booked = table.id in booked_table_ids
        tables_with_status.append(table)

    # Передаем данные в шаблон
    context = {
        'tables': tables_with_status, # Передаем список столиков с атрибутом is_booked
    }
    return render(request, 'Bookings/bookings.html', context)

@login_required
@csrf_exempt
def create_booking_view(request):
    """Обрабатывает создание бронирования через AJAX."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            table_id = data.get('table_id')
            booking_date_str = data.get('booking_date')
            booking_time_str = data.get('booking_time')
            guests_count = data.get('guests_count')
            special_requests = data.get('special_requests', '')

            # Валидация данных
            if not all([table_id, booking_date_str, booking_time_str, guests_count]):
                return JsonResponse({'success': False, 'error': 'Все поля обязательны для заполнения.'})

            # Преобразование строк в объекты даты и времени
            booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
            booking_time = datetime.strptime(booking_time_str, '%H:%M').time()
            guests_count = int(guests_count)

            # Проверка, что дата не в прошлом
            if booking_date < date.today():
                 return JsonResponse({'success': False, 'error': 'Нельзя забронировать столик на прошедшую дату.'})
            if booking_date == date.today() and booking_time < datetime.now().time():
                 return JsonResponse({'success': False, 'error': 'Нельзя забронировать столик на прошедшее время.'})

            # Проверка, что столик существует и активен
            table = Table.objects.get(pk=table_id, is_active=True)

            # Проверка, что столик не занят на это время
            existing_booking = Booking.objects.filter(
                table=table,
                booking_date=booking_date,
                booking_time=booking_time,
                status__in=['confirmed', 'pending'] # Учитываем подтвержденные и ожидающие
            ).first()

            if existing_booking:
                return JsonResponse({'success': False, 'error': 'Столик уже занят на это время.'})

            # Проверка, что количество гостей не превышает вместимость столика
            if guests_count > table.max_guests:
                 return JsonResponse({'success': False, 'error': f'Количество гостей ({guests_count}) превышает максимальную вместимость столика ({table.max_guests}).'})

            # Создание бронирования
            booking = Booking.objects.create(
                user=request.user,
                table=table,
                booking_date=booking_date,
                booking_time=booking_time,
                guests_count=guests_count,
                special_requests=special_requests
            )

            return JsonResponse({'success': True, 'message': 'Бронирование успешно создано!'})

        except Table.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Столик не найден или неактивен.'})
        except ValueError as e:
            return JsonResponse({'success': False, 'error': f'Неверный формат данных: {str(e)}'})
        except Exception as e:
            print(f"Ошибка при создании бронирования: {e}") # Логирование ошибки
            return JsonResponse({'success': False, 'error': 'Произошла ошибка при создании бронирования.'})

    return JsonResponse({'success': False, 'error': 'Недопустимый метод запроса.'})