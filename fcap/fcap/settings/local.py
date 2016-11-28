from dev import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fcap',
        'HOST': '172.17.0.2',
        'USER': 'root',
        'PASSWORD': '123456',
        'PORT': 3306,
    }
}
