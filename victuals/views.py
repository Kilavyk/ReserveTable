from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Category, MenuItem


def menu_view(request):
    """Представление для страницы меню"""
    categories = Category.objects.prefetch_related('menuitem_set').all().order_by('order')

    context = {
        'categories': categories,
    }
    return render(request, 'victuals/menu.html', context)


@login_required
def menu_management(request):
    """Управление меню для сотрудников"""
    categories = Category.objects.prefetch_related('menuitem_set').all().order_by('order')
    menu_items = MenuItem.objects.select_related('category').all().order_by('category__order', 'name')

    context = {
        'categories': categories,
        'menu_items': menu_items,
    }
    return render(request, 'victuals/menu_management.html', context)


@login_required
def add_menu_item(request):
    """Добавление новой позиции в меню"""
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            category_id = request.POST.get('category')
            dish_type = request.POST.get('dish_type', 'food')
            price = request.POST.get('price')
            weight = request.POST.get('weight')
            volume = request.POST.get('volume')
            ingredients = request.POST.get('ingredients', '')

            category = get_object_or_404(Category, id=category_id)

            menu_item = MenuItem(
                name=name,
                description=description,
                category=category,
                dish_type=dish_type,
                price=price,
                ingredients=ingredients,
                is_available=True
            )

            if weight:
                menu_item.weight = weight
            if volume:
                menu_item.volume = volume

            menu_item.save()
            messages.success(request, f'Позиция "{name}" успешно добавлена!')

        except Exception as e:
            messages.error(request, f'Ошибка при добавлении позиции: {str(e)}')

    return redirect('victuals:menu_management')


@login_required
def edit_menu_item(request):
    """Редактирование позиции меню"""
    if request.method == 'POST':
        try:
            item_id = request.POST.get('item_id')
            menu_item = get_object_or_404(MenuItem, id=item_id)

            menu_item.name = request.POST.get('name')
            menu_item.description = request.POST.get('description', '')
            menu_item.category_id = request.POST.get('category')
            menu_item.dish_type = request.POST.get('dish_type', 'food')
            menu_item.price = request.POST.get('price')
            menu_item.ingredients = request.POST.get('ingredients', '')

            # ИСПРАВЛЕННАЯ СТРОКА: правильное имя поля is_available
            menu_item.is_available = request.POST.get('is_available') == 'on'

            weight = request.POST.get('weight')
            volume = request.POST.get('volume')

            menu_item.weight = weight if weight else None
            menu_item.volume = volume if volume else None

            menu_item.save()
            messages.success(request, f'Позиция "{menu_item.name}" успешно обновлена!')

        except Exception as e:
            messages.error(request, f'Ошибка при редактировании позиции: {str(e)}')

    return redirect('victuals:menu_management')


@login_required
def delete_menu_item(request):
    """Удаление позиции меню"""
    if request.method == 'POST':
        try:
            item_id = request.POST.get('item_id')
            menu_item = get_object_or_404(MenuItem, id=item_id)
            name = menu_item.name
            menu_item.delete()
            messages.success(request, f'Позиция "{name}" успешно удалена!')

        except Exception as e:
            messages.error(request, f'Ошибка при удалении позиции: {str(e)}')

    return redirect('victuals:menu_management')