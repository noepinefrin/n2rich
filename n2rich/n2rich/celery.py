from celery import Celery

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'n2rich.settings')

app = Celery('n2rich')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

