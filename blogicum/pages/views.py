from http import HTTPStatus

from django.shortcuts import render
from django.views.generic import TemplateView


def csrf_failure(request, reason=''):
    """Ошибка CSRF токена."""
    return render(request, 'pages/403csrf.html', status=HTTPStatus.FORBIDDEN)


def page_not_found(request, exception):
    """Страница не найдена."""
    return render(request, 'pages/404.html', status=HTTPStatus.NOT_FOUND)


def server_error(request):
    """Ошибка сервера."""
    return render(request, 'pages/500.html',
                  status=HTTPStatus.INTERNAL_SERVER_ERROR)


class AboutPageView(TemplateView):
    """О проекте."""
    template_name = 'pages/about.html'


class Rules(TemplateView):
    """Наши правила."""
    template_name = 'pages/rules.html'
