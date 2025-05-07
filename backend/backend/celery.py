from celery import Celery

app = Celery('LeaseMatch')
app.conf.beat_schedule = {
    'process-scheduled-deletions-daily': {
        'task': 'account_management.tasks.process_scheduled_deletions_task',
        'schedule': 86400.0,  # Run once every 24 hours
    },
}

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()