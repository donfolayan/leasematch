from django.urls import path, include
from .views import (
    schedule_user_deletion,
    cancel_scheduled_deletion,
    process_scheduled_deletions
)

urlpatterns = [
    path('schedule-user-deletion/', schedule_user_deletion, name='schedule_user_deletion'),
    path('cancel-scheduled-deletion/', cancel_scheduled_deletion, name='cancel_scheduled_deletion'),
    path('process-scheduled-deletions/', process_scheduled_deletions, name='process_scheduled_deletions'),
]