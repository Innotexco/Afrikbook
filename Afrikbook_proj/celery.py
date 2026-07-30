"""
Celery application for Afrikbook.

Start a worker (from project root, with venv active):

    celery -A Afrikbook_proj worker -l info

On Windows use:

    celery -A Afrikbook_proj worker -l info --pool=solo
"""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Afrikbook_proj.settings")

app = Celery("Afrikbook_proj")

# Read CELERY_* settings from Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks.py in all installed apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
