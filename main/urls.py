from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Главная страница
    path('login/', views.login_view, name='login'),  # Страница логина
    path('profile/', views.profile, name='profile'),
    path('register/', views.register_view, name='register'),  # Страница регистрации
    path('book/<int:id>/', views.book_detail, name='book_detail'),  # Страница с подробной информацией о книге
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('book_list/', views.book_list, name='book_list'),
    path('edit_book/<int:bookid>/', views.edit_book, name='edit_book'),
    path('delete_book/<int:bookid>/', views.delete_book, name='delete_book'),
    path('load_categories/', views.load_categories, name='load_categories'),
    path('load_genres/', views.load_genres, name='load_genres'),
    path('load_authors/', views.load_authors, name='load_authors'),
    path('authors_list/', views.authors_list, name='authors_list'),  # Список авторов
    path('add_author/', views.add_author, name='add_author'),  # Путь для добавления автора
    path('edit_author/<int:authorid>/', views.edit_author, name='edit_author'),  # Путь для редактирования автора
    path('delete_author/<int:authorid>/', views.delete_author, name='delete_author'),  # Путь для удаления автора
    path('categories_list/', views.categories_list, name='categories_list'),  # Список категорий
    path('add_category/', views.add_category, name='add_category'),
    path('edit_category/<int:categoryid>/', views.edit_category, name='edit_category'),
    path('delete_category/<int:categoryid>/', views.delete_category, name='delete_category'),
    path('genres_list/', views.genres_list, name='genres_list'),
    path('add_genre/', views.add_genre, name='add_genre'),
    path('edit_genre/<int:genreid>/', views.edit_genre, name='edit_genre'),  # Добавьте этот маршрут
    path('delete_genre/<int:genreid>/', views.delete_genre, name='delete_genre'),
    path('borrowed_books_list/', views.borrowed_books_list, name='borrowed_books_list'),  # Одолженные книги
    path('return_book/<int:loan_id>', views.return_book, name='return_book'),
    path('fines_list/', views.fines_list, name='fines_list'),  # Штрафы
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:review_id/delete/>', views.delete_review, name='delete_review'),
    path('django_select2/', include('django_select2.urls', namespace='django_select2')),
]
