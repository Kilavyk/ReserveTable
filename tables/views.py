from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from .models import Table


@login_required
@permission_required('tables.view_table', raise_exception=True)
def tables_management_view(request):
    """Страница управления столиками"""
    # Получаем все столики, отсортированные по номеру
    tables_list = Table.objects.all().order_by('number')

    # Пагинация - 9 столиков на страницу (3x3 grid)
    paginator = Paginator(tables_list, 9)
    page_number = request.GET.get('page')
    tables = paginator.get_page(page_number)

    context = {
        'tables': tables,
    }
    return render(request, 'Tables/tables_management.html', context)


@login_required
@permission_required('tables.add_table', raise_exception=True)
def add_table_view(request):
    """Добавление нового столика"""
    if request.method == 'POST':
        try:
            number = request.POST.get('number', '').strip()
            max_guests = int(request.POST.get('max_guests', 2))
            description = request.POST.get('description', '').strip()
            is_active = request.POST.get('is_active') == 'on'

            # Валидация
            if not number:
                messages.error(request, 'Номер столика обязателен для заполнения.')
                return redirect('tables:management')

            if max_guests < 1 or max_guests > 10:
                messages.error(request, 'Количество гостей должно быть от 1 до 10.')
                return redirect('tables:management')

            # Создаем столик
            table = Table.objects.create(
                number=number,
                max_guests=max_guests,
                description=description if description else None,
                is_active=is_active
            )

            messages.success(request, f'Столик №{table.number} успешно добавлен!')

        except IntegrityError:
            messages.error(request, f'Столик с номером {number} уже существует.')
        except ValueError as e:
            messages.error(request, f'Ошибка в данных: {str(e)}')
        except Exception as e:
            messages.error(request, f'Произошла ошибка при добавлении столика: {str(e)}')

    return redirect('tables:management')


@login_required
@permission_required('tables.change_table', raise_exception=True)
def edit_table_view(request):
    """Редактирование столика"""
    if request.method == 'POST':
        try:
            table_id = request.POST.get('table_id')
            number = request.POST.get('number', '').strip()
            max_guests = int(request.POST.get('max_guests', 2))
            description = request.POST.get('description', '').strip()
            is_active = request.POST.get('is_active') == 'on'

            # Получаем столик
            table = get_object_or_404(Table, id=table_id)

            # Валидация
            if not number:
                messages.error(request, 'Номер столика обязателен для заполнения.')
                return redirect('tables:management')

            if max_guests < 1 or max_guests > 10:
                messages.error(request, 'Количество гостей должно быть от 1 до 10.')
                return redirect('tables:management')

            # Проверяем, не занят ли номер другим столиком
            if Table.objects.filter(number=number).exclude(id=table_id).exists():
                messages.error(request, f'Столик с номером {number} уже существует.')
                return redirect('tables:management')

            # Обновляем столик
            table.number = number
            table.max_guests = max_guests
            table.description = description if description else None
            table.is_active = is_active
            table.save()

            messages.success(request, f'Столик №{table.number} успешно обновлен!')

        except Table.DoesNotExist:
            messages.error(request, 'Столик не найден.')
        except ValueError as e:
            messages.error(request, f'Ошибка в данных: {str(e)}')
        except Exception as e:
            messages.error(request, f'Произошла ошибка при обновлении столика: {str(e)}')

    return redirect('tables:management')


@login_required
@permission_required('tables.delete_table', raise_exception=True)
def delete_table_view(request):
    """Удаление столика"""
    if request.method == 'POST':
        try:
            table_id = request.POST.get('table_id')
            table = get_object_or_404(Table, id=table_id)
            table_number = table.number

            # Удаляем столик
            table.delete()

            messages.success(request, f'Столик №{table_number} успешно удален!')

        except Table.DoesNotExist:
            messages.error(request, 'Столик не найден.')
        except Exception as e:
            messages.error(request, f'Произошла ошибка при удалении столика: {str(e)}')

    return redirect('tables:management')