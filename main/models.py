# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django_select2.forms import ModelSelect2Widget


class Authors(models.Model):
    authorid = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    middlename = models.CharField(max_length=100, blank=True, null=True)
    biography = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'authors'


class Bookcategories(models.Model):
    categoryid = models.AutoField(primary_key=True)
    categoryname = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'bookcategories'


class Bookcategorymapping(models.Model):
    bookid = models.OneToOneField('Books', models.DO_NOTHING, db_column='bookid', primary_key=True)  # The composite primary key (bookid, categoryid) found, that is not supported. The first column is selected.
    categoryid = models.ForeignKey(Bookcategories, models.DO_NOTHING, db_column='categoryid')

    class Meta:
        managed = False
        db_table = 'bookcategorymapping'
        unique_together = (('bookid', 'categoryid'),)


class Bookgenremapping(models.Model):
    bookid = models.OneToOneField('Books', models.DO_NOTHING, db_column='bookid', primary_key=True)  # The composite primary key (bookid, genreid) found, that is not supported. The first column is selected.
    genreid = models.ForeignKey('Bookgenres', models.DO_NOTHING, db_column='genreid')

    class Meta:
        managed = False
        db_table = 'bookgenremapping'
        unique_together = (('bookid', 'genreid'),)


class Bookgenres(models.Model):
    genreid = models.AutoField(primary_key=True)
    genrename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'bookgenres'


class Bookloans(models.Model):
    loanid = models.AutoField(primary_key=True)
    bookid = models.ForeignKey('Books', models.DO_NOTHING, db_column='bookid')
    userid = models.ForeignKey('Users', models.DO_NOTHING, db_column='userid')
    loandate = models.DateTimeField()
    returndate = models.DateTimeField(blank=True, null=True)
    isreturned = models.BooleanField(blank=True, null=True)
    renewalscount = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bookloans'


class Books(models.Model):
    bookid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    authorid = models.ForeignKey(Authors, models.DO_NOTHING, db_column='authorid')
    publicationyear = models.IntegerField(blank=True, null=True)
    totalcopies = models.IntegerField()
    availablecopies = models.IntegerField()
    image_url = models.URLField(max_length=1024, null=True, blank=True)  # Поле для ссылки на изображение

    class Meta:
        managed = False
        db_table = 'books'


class Fines(models.Model):
    fineid = models.AutoField(primary_key=True)
    userid = models.ForeignKey('Users', models.DO_NOTHING, db_column='userid')
    loanid = models.ForeignKey(Bookloans, models.DO_NOTHING, db_column='loanid')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    ispaid = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fines'


class Paymentmethods(models.Model):
    paymentid = models.AutoField(primary_key=True)
    userid = models.ForeignKey('Users', models.DO_NOTHING, db_column='userid')
    cardnumber = models.CharField(max_length=16)
    expirydate = models.DateField()
    cvv = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'paymentmethods'


class Reviews(models.Model):
    reviewid = models.AutoField(primary_key=True)
    bookid = models.ForeignKey(Books, models.DO_NOTHING, db_column='bookid')
    userid = models.ForeignKey('Users', models.DO_NOTHING, db_column='userid')
    reviewtext = models.CharField(max_length=1000, blank=True, null=True)
    reviewdate = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'reviews'


class Roles(models.Model):
    roleid = models.AutoField(primary_key=True)
    rolename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'roles'


class Userlogs(models.Model):
    logid = models.AutoField(primary_key=True)
    userid = models.ForeignKey('Users', models.DO_NOTHING, db_column='userid')
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'userlogs'


class Users(models.Model):
    userid = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    middlename = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(unique=True, max_length=255)
    passwordhash = models.CharField(max_length=255)
    phonenumber = models.CharField(max_length=20, blank=True, null=True)
    roleid = models.ForeignKey(Roles, models.DO_NOTHING, db_column='roleid')

    class Meta:
        managed = False
        db_table = 'users'

class AuthorSelect2Widget(ModelSelect2Widget):
    model = Authors
    search_fields = ['full_name__icontains']