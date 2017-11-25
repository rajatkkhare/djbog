from django.db import models


class CharField(models.Field):
    def db_type(self, connection):
        return 'char'


class TextField(models.Field):
    def db_type(self, connection):
        return 'text'
