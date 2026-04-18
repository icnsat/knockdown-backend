"""
WSGI config for knockdown project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
import subprocess

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knockdown.settings')

# Выполнить скрипты при запуске на Vercel (runtime)
if os.environ.get('VERCEL_ENV'):
    subprocess.run([sys.executable, 'manage.py', 'makemigrations', 'users'], check=False)
    subprocess.run([sys.executable, 'manage.py', 'makemigrations', 'lessons'], check=False)
    subprocess.run([sys.executable, 'manage.py', 'makemigrations', 'stats'], check=False)
    subprocess.run([sys.executable, 'manage.py', 'makemigrations'], check=False)
    subprocess.run([sys.executable, 'manage.py', 'migrate', 'users'], check=False)
    subprocess.run([sys.executable, 'manage.py', 'migrate', 'lessons'], check=False)
    subprocess.run([sys.executable, 'manage.py', 'migrate', 'stats'], check=False)
    subprocess.run([sys.executable, 'manage.py', 'migrate'], check=False)
    subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput', '--clear'], check=False)
    subprocess.run([sys.executable, 'scripts/populate_dictionary.py'], check=False)


application = get_wsgi_application()

app = application

from whitenoise import WhiteNoise
application = WhiteNoise(application, root='staticfiles')
