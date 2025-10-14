from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render

from .models import Table


def _validate_table_data(number, max_guests):
    """Валидация данных столика"""
    errors = []

    if not number:
        errors.append("Номер столика обязателен для заполнения.")

    if max_guests < 1 or max_guests > 10:
        errors.append("Количество гостей должно быть от 1 до 10.")

    return errors


def _extract_table_data_from_request(request):
    """Извлечение и базовая обработка данных столика из запроса"""
    number = request.POST.get("number", "").strip()
    max_guests = int(request.POST.get("max_guests", 2))
    description = request.POST.get("description", "").strip()
    is_active = request.POST.get("is_active") == "on"

    return number, max_guests, description, is_active


def _handle_table_operation(request, operation_type, table_id=None):
    """Обработка операций со столиками (добавление/редактирование)"""
    try:
        number, max_guests, description, is_active = _extract_table_data_from_request(
            request
        )

        # Валидация данных
        validation_errors = _validate_table_data(number, max_guests)
        if validation_errors:
            for error in validation_errors:
                messages.error(request, error)
            return redirect("tables:management")

        if operation_type == "add":
            # Создаем столик
            table = Table.objects.create(
                number=number,
                max_guests=max_guests,
                description=description if description else None,
                is_active=is_active,
            )
            success_message = f"Столик №{table.number} успешно добавлен!"

        elif operation_type == "edit":
            # Получаем столик для редактирования
            table = get_object_or_404(Table, id=table_id)

            # Проверяем, не занят ли номер другим столиком
            if Table.objects.filter(number=number).exclude(id=table_id).exists():
                messages.error(request, f"Столик с номером {number} уже существует.")
                return redirect("tables:management")

            # Обновляем столик
            table.number = number
            table.max_guests = max_guests
            table.description = description if description else None
            table.is_active = is_active
            table.save()
            success_message = f"Столик №{table.number} успешно обновлен!"

        messages.success(request, success_message)

    except IntegrityError:
        messages.error(request, f"Столик с номером {number} уже существует.")
    except ValueError as e:
        messages.error(request, f"Ошибка в данных: {str(e)}")
    except Exception as e:
        operation_name = "добавлении" if operation_type == "add" else "обновлении"
        messages.error(
            request, f"Произошла ошибка при {operation_name} столика: {str(e)}"
        )


@login_required
@permission_required("tables.view_table", raise_exception=True)
def tables_management_view(request):
    """Страница управления столиками"""
    # Получаем все столики, отсортированные по номеру
    tables_list = Table.objects.all().order_by("number")

    # Пагинация - 9 столиков на страницу
    paginator = Paginator(tables_list, 9)
    page_number = request.GET.get("page")
    tables = paginator.get_page(page_number)

    context = {
        "tables": tables,
    }
    return render(request, "tables/tables_management.html", context)


@login_required
@permission_required("tables.add_table", raise_exception=True)
def add_table_view(request):
    """Добавление нового столика"""
    if request.method == "POST":
        _handle_table_operation(request, "add")
    return redirect("tables:management")


@login_required
@permission_required("tables.change_table", raise_exception=True)
def edit_table_view(request):
    """Редактирование столика"""
    if request.method == "POST":
        table_id = request.POST.get("table_id")
        _handle_table_operation(request, "edit", table_id)
    return redirect("tables:management")


@login_required
@permission_required("tables.delete_table", raise_exception=True)
def delete_table_view(request):
    """Удаление столика"""
    if request.method == "POST":
        try:
            table_id = request.POST.get("table_id")
            table = get_object_or_404(Table, id=table_id)
            table_number = table.number

            # Удаляем столик
            table.delete()

            messages.success(request, f"Столик №{table_number} успешно удален!")

        except Table.DoesNotExist:
            messages.error(request, "Столик не найден.")
        except Exception as e:
            messages.error(request, f"Произошла ошибка при удалении столика: {str(e)}")

    return redirect("tables:management")
