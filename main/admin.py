from django.contrib import admin
from .models import Authors, Bookcategories, Bookcategorymapping, Bookgenremapping, Bookgenres, Bookloans, Books, Fines, Paymentmethods, Reviews, Roles, Userlogs, Users

class AuthorsAdmin(admin.ModelAdmin):
    list_display = ('authorid', 'firstname', 'lastname', 'middlename', 'biography')
    search_fields = ('firstname', 'lastname')
    list_filter = ('lastname',)

# Класс для модели Bookcategories
class BookcategoriesAdmin(admin.ModelAdmin):
    list_display = ('categoryid', 'categoryname')
    search_fields = ('categoryname',)

# Класс для модели Bookcategorymapping
class BookcategorymappingAdmin(admin.ModelAdmin):
    list_display = ('bookid', 'categoryid')
    list_filter = ('categoryid',)

# Класс для модели Bookgenremapping
class BookgenremappingAdmin(admin.ModelAdmin):
    list_display = ('bookid', 'genreid')
    list_filter = ('genreid',)

# Класс для модели Bookgenres
class BookgenresAdmin(admin.ModelAdmin):
    list_display = ('genreid', 'genrename')
    search_fields = ('genrename',)

# Класс для модели Bookloans
class BookloansAdmin(admin.ModelAdmin):
    list_display = ('loanid', 'bookid', 'userid', 'loandate', 'returndate', 'isreturned', 'renewalscount')
    list_filter = ('isreturned', 'bookid')
    search_fields = ('userid__firstname', 'userid__lastname', 'bookid__title')

# Класс для модели Books
class BooksAdmin(admin.ModelAdmin):
    list_display = ('bookid', 'title', 'authorid', 'publicationyear', 'totalcopies', 'availablecopies')
    list_filter = ('authorid', 'publicationyear')
    search_fields = ('title', 'authorid__firstname', 'authorid__lastname')

# Класс для модели Fines
class FinesAdmin(admin.ModelAdmin):
    list_display = ('fineid', 'userid', 'loanid', 'amount', 'ispaid')
    list_filter = ('ispaid',)
    search_fields = ('userid__firstname', 'userid__lastname')

# Класс для модели Paymentmethods
class PaymentmethodsAdmin(admin.ModelAdmin):
    list_display = ('paymentid', 'userid', 'cardnumber', 'expirydate', 'cvv')
    search_fields = ('userid__firstname', 'userid__lastname')

# Класс для модели Reviews
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ('reviewid', 'bookid', 'userid', 'reviewtext', 'reviewdate')
    search_fields = ('bookid__title', 'userid__firstname', 'userid__lastname')

# Класс для модели Roles
class RolesAdmin(admin.ModelAdmin):
    list_display = ('roleid', 'rolename')
    search_fields = ('rolename',)

# Класс для модели Userlogs
class UserlogsAdmin(admin.ModelAdmin):
    list_display = ('logid', 'userid', 'action', 'timestamp')
    search_fields = ('userid__firstname', 'userid__lastname', 'action')
    list_filter = ('timestamp',)

# Класс для модели Users
class UsersAdmin(admin.ModelAdmin):
    list_display = ('userid', 'firstname', 'lastname', 'email', 'roleid')
    search_fields = ('firstname', 'lastname', 'email')
    list_filter = ('roleid',)

# Регистрируем модели в админке
admin.site.register(Authors, AuthorsAdmin)
admin.site.register(Bookcategories, BookcategoriesAdmin)
admin.site.register(Bookcategorymapping, BookcategorymappingAdmin)
admin.site.register(Bookgenremapping, BookgenremappingAdmin)
admin.site.register(Bookgenres, BookgenresAdmin)
admin.site.register(Bookloans, BookloansAdmin)
admin.site.register(Books, BooksAdmin)
admin.site.register(Fines, FinesAdmin)
admin.site.register(Paymentmethods, PaymentmethodsAdmin)
admin.site.register(Reviews, ReviewsAdmin)
admin.site.register(Roles, RolesAdmin)
admin.site.register(Userlogs, UserlogsAdmin)
admin.site.register(Users, UsersAdmin)
