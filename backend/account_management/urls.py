from django.urls import path, include
from .views import (
    schedule_user_deletion,
    cancel_scheduled_deletion,
)

urlpatterns = [
    path('schedule_user_deletion/', schedule_user_deletion, name='schedule_user_deletion'),
    path('cancel_scheduled_deletion/', cancel_scheduled_deletion, name='cancel_scheduled_deletion'),
]