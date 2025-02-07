from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import connection
from .models import Books, Bookcategories, Bookgenres, Users, Authors, Bookloans, Fines, Bookcategorymapping, Bookgenremapping, Reviews
from django.core.paginator import Paginator
from django.contrib.auth import logout
import logging, bcrypt, requests
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q, Prefetch

logger = logging.getLogger('LibrarySystem')

def home(request):
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    genre_filter = request.GET.get('genre', '')

    books = Books.objects.all()

    if search_query:
        books = books.filter(title__icontains=search_query)

    if category_filter:
        books = books.filter(bookcategorymapping__categoryid=category_filter)

    if genre_filter:
        books = books.filter(bookgenremapping__genreid=genre_filter)

    paginator = Paginator(books, 20)  # 20 книг на страницу
    page_number = request.GET.get('page')
    books_page = paginator.get_page(page_number)

    categories = Bookcategories.objects.all()
    genres = Bookgenres.objects.all()

    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name')
    user_role = request.session.get('user_role')

    return render(request, 'home.html', {
        'books': books_page,
        'categories': categories,
        'genres': genres,
        'search_query': search_query,
        'selected_category': category_filter,
        'selected_genre': genre_filter,
        'user_id': user_id,
        'user_name': user_name,
        'user_role': user_role,
    })

def check_password(plain_password, hashed_password):
    with connection.cursor() as cursor:
        # Проверяем совпадение пароля с хешем в базе данных
        cursor.execute("SELECT crypt(%s, %s) = %s", [plain_password, hashed_password, hashed_password])
        result = cursor.fetchone()
        return result[0]  # True если пароли совпадают, иначе False

# Функция для отображения страницы логина

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        logger.info(f"Введённые данные: email={email}, password={password}")

        try:
            user = Users.objects.get(email=email)
            logger.info(f"Пользователь {email} найден.")

            if bcrypt.checkpw(password.encode('utf-8'), user.passwordhash.encode('utf-8')):
                logger.info(f"Пользователь {email} успешно авторизован.")

                # Сохранение сессионных данных
                request.session['user_id'] = user.userid
                request.session['user_name'] = f"{user.firstname} {user.lastname}"
                request.session['user_role'] = user.roleid.rolename

                # Уведомление пользователя
                messages.success(request, "Вы успешно вошли!")
                return redirect('home')  # Перенаправление на главную страницу
            else:
                logger.warning(f"Неверный пароль для пользователя {email}.")
                messages.error(request, "Неверный пароль.")
        except Users.DoesNotExist:
            logger.warning(f"Пользователь с email {email} не найден.")
            messages.error(request, "Пользователь с таким email не существует.")
        except Exception as e:
            logger.error(f"Ошибка при авторизации: {e}")
            messages.error(request, f"Ошибка при авторизации: {e}")

    return render(request, 'login.html')

# Функция для отображения страницы регистрации
def register_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        middle_name = request.POST.get("middle_name", "").strip() or None  # None если пустое
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        phone = request.POST.get('phone') or None

        # Выводим данные в консоль перед отправкой в запрос
        print(f"First Name: {first_name}, Last Name: {last_name}, Email: {email}, Password: {password}, Middle Name: {middle_name}, Phone: {phone}")

        # Проверка на длину пароля
        if len(password) > 25:
            messages.error(request, "Пароль не должен быть длиннее 25 символов.")
            return redirect("register")

        # Отправка данных в PostgreSQL через хранимую процедуру
        try:
            print(first_name, last_name, email, password, phone)
            with connection.cursor() as cursor:
                cursor.execute("CALL adduser(%s, %s, %s, %s, %s, %s)",
                               [first_name, last_name,email, password, middle_name, phone])  # Пароль в открытом виде
            messages.success(request, "Регистрация прошла успешно! Теперь можно войти.")
            return redirect("login")  # Перенаправление на страницу входа
        except Exception as e:
            messages.error(request, f"Ошибка: {e}")

    return render(request, "register.html")

# Функция для отображения страницы с подробной информацией о книге
def book_detail(request, book_id):
    # Получаем объект книги по id, если книга не найдена - возвращаем 404 ошибку
    book = get_object_or_404(Books, id=book_id)
    return render(request, 'book_detail.html', {'book': book})

def forgot_password(request):
    return render(request, 'forgot_password.html')

def logout_view(request):
    logout(request)  # Очистка сессии пользователя
    messages.success(request, "Вы успешно вышли!")
    return redirect('home')  # Перенаправление на главную страницу


def profile(request):
    if 'user_id' not in request.session:  # Проверка по сессии
        return redirect('login')  # Перенаправление на страницу входа, если пользователь не авторизован через сессию

    # Получаем данные пользователя из сессии
    user_id = request.session['user_id']
    user = Users.objects.get(userid=user_id)
    role = user.roleid  # Получаем роль пользователя

    context = {
        'user': user,
        'role': role
    }

    return render(request, 'profile.html', context)  # Отображаем страницу профиля и передаем роль

def get_access_token():
    """Функция для получения актуального access_token через refresh_token"""
    client_id = "5040ba1685b8ed5"
    client_secret = "29995bc9ff205387c089b70eadbc5c614c4c81a7"
    refresh_token = "285f8ce4c1d716360df7485073e4110b155d0bc5"

    token_url = "https://api.imgur.com/oauth2/token"
    data = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
    }

    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("Ошибка получения access_token:", response.json())
        return None

def upload_image_to_imgur(image):
    """Загружает изображение в Imgur и возвращает ссылку"""
    access_token = get_access_token()
    if not access_token:
        print("Ошибка: access_token не получен")
        return None

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    files = {
        "image": image
    }

    # Отправляем запрос к API Imgur
    response = requests.post("https://api.imgur.com/3/upload", headers=headers, files=files)

    if response.status_code == 200:
        return response.json()["data"]["link"]  # Возвращаем ссылку на изображение
    else:
        print("Ошибка загрузки изображения:", response.json())
        return None

def book_list(request):
    # Проверка прав пользователя
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    user = Users.objects.get(userid=user_id)
    role = user.roleid  # Получаем роль пользователя

    # Получаем все книги
    books = Books.objects.all()

    # Получаем данные для выпадающих списков
    authors = Authors.objects.all()
    authors_with_full_name = [
        {'id': author.authorid, 'full_name': f"{author.firstname} {author.middlename} {author.lastname}".strip()}
        for author in authors
    ]
    categories = Bookcategories.objects.all()
    genres = Bookgenres.objects.all()

    # Обработка POST запроса (для добавления и удаления книг)
    if request.method == 'POST':
        if 'add_book' in request.POST:
            title = request.POST.get('title')
            author_id = request.POST.get('author')
            publicationyear = request.POST.get('publicationyear')

            # Преобразуем строку вида 'YYYY-MM-DD' в год
            publicationyear = int(publicationyear.split('-')[0]) if publicationyear else None

            totalcopies = request.POST.get('totalcopies')
            availablecopies = request.POST.get('availablecopies')
            image = request.FILES.get('image')
            category_ids = request.POST.getlist('categories')
            genre_ids = request.POST.getlist('genres')

            # Загружаем изображение на Imgur (если требуется)
            image_url = None
            if image:
                image_url = upload_image_to_imgur(image)

            # Создаем новую книгу
            author = Authors.objects.get(authorid=author_id)
            new_book = Books(
                title=title,
                authorid=author,
                publicationyear=publicationyear,
                totalcopies=totalcopies,
                availablecopies=availablecopies,
                image_url=image_url
            )
            new_book.save()

            # Связываем категории и жанры с книгой
            selected_categories = Bookcategories.objects.filter(categoryid__in=category_ids)
            selected_genres = Bookgenres.objects.filter(genreid__in=genre_ids)

            # new_book.categories.set(selected_categories)
            # new_book.genres.set(selected_genres)

            new_book.save()

            # Добавляем связи в промежуточные таблицы
            for category in selected_categories:
                Bookcategorymapping.objects.create(bookid=new_book, categoryid=category)

            for genre in selected_genres:
                Bookgenremapping.objects.create(bookid=new_book, genreid=genre)

            new_book.save()  # Сохраняем книгу снова (если нужно)

            return redirect('book_list')  # Перезагружаем страницу с книгами

        elif 'delete_book' in request.POST:
            # Удаление книги
            bookid = request.POST.get('bookid')
            book = get_object_or_404(Books, bookid=bookid)
            book.delete()
            return redirect('book_list')

    # Если метод GET, показываем страницу с книгами
    context = {
        'books': books,
        'role': role,
        'authors': authors_with_full_name,
        'categories': categories,
        'genres': genres
    }

    return render(request, 'book_list.html', context)


def edit_book(request, bookid):
    # Проверка сессии на наличие пользователя
    if 'user_id' not in request.session:  # Если пользователь не авторизован
        return redirect('login')  # Перенаправление на страницу входа

    # Получаем данные пользователя из сессии
    user_id = request.session['user_id']
    user = Users.objects.get(userid=user_id)  # Получаем пользователя по ID
    role = user.roleid  # Получаем роль пользователя

    # Если роль не "Менеджер", перенаправляем на главную страницу
    if role.rolename != 'Менеджер':
        return redirect('home')  # Редирект на главную страницу

    # Получаем книгу для редактирования
    book = get_object_or_404(Books, bookid=bookid)

    # Загружаем авторов, категорий и жанров для формы
    authors = Authors.objects.all()
    authors_with_full_name = [
        {'id': author.authorid, 'full_name': f"{author.firstname} {author.middlename} {author.lastname}".strip()}
        for author in authors
    ]
    categories = Bookcategories.objects.all()  # Получаем все категории
    genres = Bookgenres.objects.all()  # Получаем все жанры

    if request.method == 'POST':
        title = request.POST.get('title')
        authorid = request.POST.get('authorid')
        publicationyear = request.POST.get('publicationyear')
        totalcopies = request.POST.get('totalcopies')
        availablecopies = request.POST.get('availablecopies')
        image = request.FILES.get('image')

        if publicationyear:
            # Преобразуем строку в год (например, '2023-02-07' -> 2023)
            publicationyear = publicationyear.split('-')[0]

        # Загружаем изображение на Imgur
        image_url = book.image_url  # оставляем старое изображение, если новое не загружено
        if image:
            image_url = upload_image_to_imgur(image)

        # Обновляем данные книги
        book.title = title
        book.authorid = Authors.objects.get(authorid=authorid)
        book.publicationyear = publicationyear
        book.totalcopies = totalcopies
        book.availablecopies = availablecopies
        book.image_url = image_url
        book.save()

        return redirect('book_list')

    return render(request, 'edit_book.html', {
        'book': book,
        'role': role,
        'authors': authors_with_full_name,
        'categories': categories,
        'genres': genres,
    })

def delete_book(request, bookid):
    # Проверка авторизации пользователя
    if 'user_id' not in request.session:
        return redirect('login')

    user = Users.objects.get(userid=request.session['user_id'])
    if user.roleid.rolename != 'Менеджер':
        return HttpResponseForbidden("У вас нет доступа к этому разделу.")

    book = get_object_or_404(Books, bookid=bookid)
    book.delete()  # Удаляем книгу

    return redirect('book_list')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.timezone import now, timedelta
from .models import Books, Users, Bookloans

def book_detail(request, id):
    # Получаем книгу
    book = get_object_or_404(Books, bookid=id)

    categories = Bookcategorymapping.objects.filter(bookid=book)
    genres = Bookgenremapping.objects.filter(bookid=book)

    # Проверяем авторизацию пользователя
    user = None
    user_role = None
    if 'user_id' in request.session:
        user = Users.objects.get(userid=request.session['user_id'])
        user_role = user.roleid.rolename  # Предполагается, что роль связана через ForeignKey

    reviews = Reviews.objects.filter(bookid=book)

    if request.method == "POST":
        action = request.POST.get('action')

        if action == "add_review" and user_role == "Гость":
            # Добавление отзыва
            review_text = request.POST.get('reviewtext')
            Reviews.objects.create(
                bookid=book,
                userid=user,
                reviewtext=review_text,
                reviewdate=now()
            )
            messages.success(request, "Ваш отзыв успешно добавлен.")
            return redirect('book_detail', id=id)

        elif action == "take_book" and user_role == "Гость":
            # Если книга доступна, уменьшаем количество доступных копий
            if book.availablecopies > 0:
                book.availablecopies -= 1
                book.save()

                # Создаем запись в Bookloans
                Bookloans.objects.create(
                    userid=user,
                    bookid=book,
                    loandate=now(),
                    returndate=now() + timedelta(days=14),
                    isreturned=False,
                    renewalscount=0
                )

                messages.success(request, "Вы успешно взяли книгу. Верните её в течение 14 дней.")
                return redirect('book_detail', id=id)
            else:
                messages.error(request, "Книга недоступна.")
                return redirect('book_detail', id=id)

    return render(request, 'book_detail.html', {
        'book': book,
        'categories': categories,
        'genres': genres,
        'user': user,
        'user_role': user_role,
        'reviews': reviews
    })

# Дополнительные views для подгрузки категорий и жанров
def load_categories(request):
    query = request.GET.get('q', '')
    categories = Bookcategories.objects.filter(categoryname__icontains=query)
    data = [{'id': category.categoryid, 'text': category.categoryname} for category in categories]
    return JsonResponse(data, safe=False)

def load_genres(request):
    query = request.GET.get('q', '')
    genres = Bookgenres.objects.filter(genrename__icontains=query)
    data = [{'id': genre.genreid, 'text': genre.genrename} for genre in genres]
    return JsonResponse(data, safe=False)

def load_authors(request):
    query = request.GET.get('q', '')
    authors = Authors.objects.filter(full_name__icontains=query)  # Фильтруем авторов по имени
    data = [{'id': author.id, 'text': author.full_name} for author in authors]
    return JsonResponse(data, safe=False)

def authors_list(request):
    if 'user_id' not in request.session:  # Проверка по сессии
        return redirect('login')  # Перенаправление на страницу входа, если пользователь не авторизован через сессию

    user_id = request.session['user_id']
    try:
        user = Users.objects.get(userid=user_id)
        role = user.roleid  # Получаем роль пользователя
    except Users.DoesNotExist:
        return redirect('login')

    # Получаем список авторов
    search_query = request.GET.get('search', '')
    authors = Authors.objects.all()

    if search_query:
        authors = authors.filter(
            Q(firstname__icontains=search_query) |
            Q(lastname__icontains=search_query) |
            Q(middlename__icontains=search_query)
        )

    # Пагинация: выводим по 5 авторов
    authors_per_page = 5
    page = request.GET.get('page', 1)
    start = (int(page) - 1) * authors_per_page
    end = start + authors_per_page
    authors = authors[start:end]

    # Количество страниц
    total_authors = authors.count()
    total_pages = (total_authors // authors_per_page) + (1 if total_authors % authors_per_page > 0 else 0)

    # Проверка на AJAX запрос
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Проверяем заголовок для AJAX
        return JsonResponse({'authors': list(authors.values())})

    return render(request, 'authors_list.html', {'role': role, 'authors': authors, 'search_query': search_query})

# Представление для добавления автора
def add_author(request):
    if request.method == 'POST':
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        middlename = request.POST['middlename']
        biography = request.POST['biography']

        # Создаем нового автора
        new_author = Authors(
            firstname=firstname,
            lastname=lastname,
            middlename=middlename,
            biography=biography
        )
        new_author.save()
        return redirect('authors_list')  # Перенаправляем на список авторов после добавления

# Представление для редактирования автора
def edit_author(request, authorid):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    user = Users.objects.get(userid=user_id)
    role = user.roleid

    # Получаем автора по ID
    author = get_object_or_404(Authors, authorid=authorid)

    if request.method == 'POST':
        # Обновляем данные автора
        author.firstname = request.POST.get('firstname')
        author.lastname = request.POST.get('lastname')
        author.middlename = request.POST.get('middlename')
        author.biography = request.POST.get('biography')
        author.save()
        return redirect('authors_list')

    return render(request, 'edit_author.html', {'author': author, 'role': role})

# Представление для удаления автора
def delete_author(request, authorid):
    author = Authors.objects.get(authorid=authorid)
    author.delete()
    return redirect('authors_list')

# Список категорий
def categories_list(request):
    # Проверка сессии на наличие пользователя
    if 'user_id' not in request.session:  # Если пользователь не авторизован
        return redirect('login')  # Перенаправление на страницу входа

    # Получаем данные пользователя из сессии
    user_id = request.session['user_id']
    user = Users.objects.get(userid=user_id)  # Получаем пользователя по ID
    role = user.roleid  # Получаем роль пользователя

    # Если роль не "Менеджер", перенаправляем на главную страницу
    if role.rolename != 'Менеджер':
        return redirect('home')  # Редирект на главную страницу

    # Поиск категорий
    search_query = request.GET.get('search', '')
    categories = Bookcategories.objects.all()

    if search_query:
        categories = categories.filter(
            Q(categoryname__icontains=search_query)  # Фильтрация по имени категории
        )

    if request.method == 'POST':
        # Добавление новой категории
        categoryname = request.POST.get('categoryname')
        Bookcategories.objects.create(categoryname=categoryname)
        return redirect('categories_list')  # Перенаправление на страницу списка категорий

    return render(request, 'categories_list.html', {'categories': categories, 'search_query': search_query, 'role': role})

def add_category(request):
    if request.method == 'POST':
        categoryname = request.POST.get('categoryname')
        Bookcategories.objects.create(categoryname=categoryname)
        return redirect('categories_list')
    return render(request, 'add_category.html')

def edit_category(request, categoryid):
    if 'user_id' not in request.session:
        return redirect('login')  # Если пользователь не авторизован, перенаправляем на страницу входа

    user = Users.objects.get(userid=request.session['user_id'])  # Извлекаем пользователя по user_id из сессии

    if user.roleid.rolename != 'Менеджер':
        return HttpResponseForbidden("У вас нет доступа к этому разделу.")  # Если не менеджер, доступ запрещен

    category = get_object_or_404(Bookcategories, categoryid=categoryid)

    if request.method == 'POST':
        category.categoryname = request.POST['categoryname']
        category.save()
        return redirect('categories_list')

    return render(request, 'edit_category.html', {'category': category, 'user': user})


# Список жанров

def delete_category(request, categoryid):
    category = get_object_or_404(Bookcategories, categoryid=categoryid)
    category.delete()
    return redirect('categories_list')


def genres_list(request):
    # Проверка сессии на наличие пользователя
    if 'user_id' not in request.session:
        return redirect('login')  # Если пользователь не авторизован, перенаправляем на страницу входа

    # Получаем данные пользователя из сессии
    user_id = request.session['user_id']
    user = Users.objects.get(userid=user_id)  # Получаем пользователя по ID
    role = user.roleid  # Получаем роль пользователя

    # Если роль не "Менеджер", перенаправляем на главную страницу
    if role.rolename != 'Менеджер':
        return redirect('home')  # Редирект на главную страницу

    # Поиск жанров
    search_query = request.GET.get('search', '')
    genres = Bookgenres.objects.all()

    if search_query:
        genres = genres.filter(
            Q(genrename__icontains=search_query)  # Фильтрация по имени жанра
        )

    if request.method == 'POST':
        # Добавление нового жанра
        genrename = request.POST.get('genrename')
        Bookgenres.objects.create(genrename=genrename)
        return redirect('genres_list')  # Перенаправление на страницу списка жанров

    return render(request, 'genres_list.html', {'genres': genres, 'search_query': search_query, 'role': role})

def add_genre(request):
    if request.method == 'POST':
        genrename = request.POST.get('genrename')
        Bookgenres.objects.create(genrename=genrename)
        return redirect('genres_list')
    return render(request, 'add_genre.html')

from django.shortcuts import get_object_or_404

def edit_genre(request, genreid):
    if 'user_id' not in request.session:
        return redirect('login')  # Если пользователь не авторизован, перенаправляем на страницу входа

    user = Users.objects.get(userid=request.session['user_id'])  # Извлекаем пользователя по user_id из сессии

    if user.roleid.rolename != 'Менеджер':
        return HttpResponseForbidden("У вас нет доступа к этому разделу.")  # Если не менеджер, доступ запрещен

    genre = get_object_or_404(Bookgenres, genreid=genreid)

    if request.method == 'POST':
        genre.genrename = request.POST['genrename']
        genre.save()
        return redirect('genres_list')

    return render(request, 'edit_genre.html', {'genre': genre, 'user': user, 'role': user.roleid})  # Передаем роль пользователя

def delete_genre(request, genreid):
    genre = get_object_or_404(Bookgenres, genreid=genreid)
    genre.delete()
    return redirect('genres_list')

# Список одолженных книг
def borrowed_books_list(request):
    search_query = request.GET.get('search', '')  # Получаем значение поискового запроса
    borrowed_books = Bookloans.objects.filter(isreturned=False)  # Получаем все одолженные книги (не возвращенные)
    user_id = request.session['user_id']
    user = Users.objects.get(userid=user_id)  # Получаем пользователя по ID
    role = user.roleid  # Получаем роль пользователя

    if search_query:
        borrowed_books = Bookloans.objects.filter(
            isreturned=False

        ).filter(
            Q(userid__firstname__icontains=search_query) |
            Q(userid__lastname__icontains=search_query) |
            Q(userid__email__icontains=search_query) |
            Q(userid__phonenumber__icontains=search_query)
        )
    else:
        borrowed_books = Bookloans.objects.filter(isreturned=False)  # Получаем все одолженные книги (не возвращенные)

    return render(request, 'borrowed_books_list.html', {
        'borrowed_books': borrowed_books,
        'search_query': search_query,
        'role': role,
        'user': user,
        'userid': user_id,
    })


def return_book(request, loan_id):
    try:
        loan = Bookloans.objects.get(loanid=loan_id)
    except Bookloans.DoesNotExist:
        messages.error(request, "Ошибка: заимствованная книга не найдена.")
        return redirect('borrowed_books_list')

    # Обновляем доступное количество книги
    book = loan.bookid
    book.availablecopies += 1
    book.save()

    # Удаляем запись о заимствовании
    loan.delete()

    messages.success(request, f"Книга '{book.title}' успешно возвращена.")
    return redirect('borrowed_books_list')

# Список штрафов
def fines_list(request):
    fines = Fines.objects.all()  # Получаем все штрафы из базы данных

    user_id = request.session['user_id']
    user = Users.objects.get(userid=user_id)  # Получаем пользователя по ID
    role = user.roleid  # Получаем роль пользователя

    return render(request, 'fines_list.html', {
        'fines': fines,
        'role': role,
        'user': user,
        'userid': user_id,})

def edit_review(request, review_id):
    # Получаем отзыв
    review = get_object_or_404(Reviews, reviewid=review_id)

    # Проверяем, что отзыв принадлежит текущему пользователю
    if review.userid != request.user:
        messages.error(request, "Вы не можете редактировать этот отзыв.")
        return redirect('book_detail', id=review.bookid.id)

    # Обработка формы редактирования отзыва
    if request.method == 'POST':
        review_text = request.POST.get('reviewtext')

        # Обновляем отзыв
        if review_text:
            review.reviewtext = review_text
            review.reviewdate = now()  # Обновляем дату отзыва
            review.save()

            messages.success(request, "Ваш отзыв успешно обновлен.")
            return redirect('book_detail', id=review.bookid.id)

    # Отображаем форму с текущим текстом отзыва
    return render(request, 'edit_review.html', {'review': review, 'book': review.bookid})

def delete_review(request, review_id):
    review = get_object_or_404(Reviews, reviewid=review_id)

    # Проверка, что отзыв принадлежит текущему пользователю или является администратором
    if review.userid != request.user:
        messages.error(request, "Вы не можете удалить этот отзыв.")
        return redirect('book_detail', id=review.bookid.bookid)

    # Удаляем отзыв
    review.delete()

    messages.success(request, "Отзыв успешно удален.")
    return redirect('book_detail', id=review.bookid.bookid)