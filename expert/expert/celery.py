import os
from celery import Celery
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expert.settings')

# Setup Django before creating Celery app
django.setup()

app = Celery('expert')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
