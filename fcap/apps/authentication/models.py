from __future__ import unicode_literals

from django.db import models


class User(models.Model):

    class Meta:
        app_label = 'authentication'
        db_table = 'user'

    username = models.CharField(max_length=30, unique=True, db_index=True)
    password = models.CharField(max_length=30)
    fullname = models.CharField(max_length=50)

    USERNAME_FIELD = 'username'
