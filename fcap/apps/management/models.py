from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Provider(models.Model):

    class Meta:
        db_table = 'provider'

    name = models.TextField(unique=True)
    config = models.TextField()
    description = models.TextField()
    username = models.ForeignKey(User)

    USERNAME_FIELD = 'name'


class Network(models.Model):

    class Meta:
        db_table = 'network'

    name = models.TextField(unique=True)
    description = models.TextField()
    network_id = models.TextField(unique=True, db_index=True)
    cidr = models.TextField()
    cloud = models.TextField()
    gateway = models.TextField()
    security_group = models.TextField()
    allocation_pools = models.TextField()
    dns_nameservers = models.TextField()

    USERNAME_FIELD = 'network_id'


class Instance(models.Model):

    class Meta:
        db_table = 'instance'
