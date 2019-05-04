from .base import *

DEBUG = True

INSTALLED_APPS += [
    'django_extensions'
]

# django_extensions config
SHELL_PLUS = 'ipython'
SHELL_PLUS_POST_IMPORTS = [
    ('core', ('twitch', 'tasks')),
]
