from django.shortcuts import redirect
from django.urls import reverse

class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Исключаем страницы, которые не требуют авторизации
        exempt_urls = [
            reverse('register'),
            reverse('login'),
            '/',  # index page
        ]
        
        if not request.user.is_authenticated and request.path not in exempt_urls:
            return redirect('index')
        
        response = self.get_response(request)
        return response