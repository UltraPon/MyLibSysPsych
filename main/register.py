import logging
import re
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db import connection

logger = logging.getLogger('LibrarySystem')

def is_valid_name(value):
    """Функция проверки имени, фамилии и отчества"""
    return bool(re.fullmatch(r"^[A-Za-zА-Яа-яЁё\s-]{1,50}$", value))

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        middle_name = request.POST.get('middle_name', '').strip() or None
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        phone = request.POST.get('phone') or None

        # Проверка, что email не пустой
        if not email:
            messages.error(request, "Поле Email обязательно для заполнения.")
            return redirect('register')

        # Проверка имени и фамилии
        if not first_name or not last_name or not is_valid_name(first_name) or not is_valid_name(last_name):
            messages.error(request, "Имя и фамилия обязательны и должны содержать только буквы.")
            return redirect('register')

        # Проверка пароля
        if not password:
            messages.error(request, "Пароль обязателен для заполнения.")
            return redirect('register')

        if len(password) > 25:
            messages.error(request, "Пароль не должен быть длиннее 25 символов.")
            return redirect('register')

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL adduser(%s, %s, %s, %s, %s, %s)",
                    [first_name, last_name, middle_name, email, password, phone]  # Передаём пароль в открытом виде
                )

            messages.success(request, "Регистрация успешна! Теперь можно войти.")
            logger.info(f"Пользователь {email} зарегистрирован.")
            return redirect('login')

        except Exception as e:
            logger.error(f"Ошибка при регистрации пользователя {email}: {e}")
            messages.error(request, f"Ошибка при регистрации: {e}")  # Можно отключить, если не хочешь выводить ошибку пользователю
            return redirect('register')

    return render(request, 'register.html')