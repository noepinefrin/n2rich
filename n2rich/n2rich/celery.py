import os
from celery import Celery, Task


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'n2rich.settings')

app = Celery('n2rich')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

