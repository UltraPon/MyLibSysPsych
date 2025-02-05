import bcrypt
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Users  # Импортируем модель User

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Ищем пользователя по email
            user = Users.objects.get(email=email)

            # Проверяем пароль с помощью bcrypt
            if bcrypt.checkpw(password.encode('utf-8'), user.passwordhash.encode('utf-8')):
                # Успешная авторизация
                request.session['user_id'] = user.id  # Сохраняем id пользователя в сессии
                request.session['user_name'] = f"{user.firstname} {user.lastname}"  # Сохраняем имя пользователя
                request.session['user_role'] = user.roleid.rolename  # Сохраняем роль пользователя
                messages.success(request, "Вы успешно вошли!")
                return redirect('home')  # Перенаправляем на главную страницу
            else:
                messages.error(request, "Неверный пароль.")
        except Users.DoesNotExist:
            messages.error(request, "Пользователь с таким email не существует.")
        except Exception as e:
            messages.error(request, f"Ошибка при авторизации: {e}")

    return render(request, 'login.html')  # Возвращаем страницу авторизации