from django.shortcuts import render
from .models import Category


def menu_view(request):
    """Представление для страницы меню"""
    categories = Category.objects.prefetch_related('menuitem_set').all().order_by('order')

    context = {
        'categories': categories,
    }
    return render(request, 'victuals/menu.html', context)
