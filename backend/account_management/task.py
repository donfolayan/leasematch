from celery import shared_task
from backend.utils.email import send_email
from authentication.models import CustomUser, ScheduledDeletion
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

@shared_task
def process_scheduled_deletions_task():
    """
    Celery task to process scheduled deletions.
    """
    scheduled_deletions = ScheduledDeletion.objects.filter(cancelled=False, scheduled_for__lte=now())
    for deletion in scheduled_deletions:
        deletion.delete()
    return "Scheduled deletions processed successfully."

@shared_task
def send_inactive_user_email(user_id, email, reactivation_url):
    """
    Celery task to send email to inactive users.
    """
    send_email(
        subject="Inactive Account Scheduled for Deletion",
        message=(
            f"Dear User,\n\n"
            f"Your account has been marked as inactive and is scheduled for deletion in 20 days. "
            f"If you wish to keep your account, please click the link below to reactivate it:\n\n"
            f"{reactivation_url}\n\n"
            f"If you do not take any action, your account will be deleted automatically."
        ),
        recipient_list=[email],
    )
    return "Email sent successfully."

@shared_task
def process_inactive_user_deletions_task():
    """
    Celery task to process inactive users and schedule deletions.
    """
    inactive_users = CustomUser.objects.filter(is_active=False)
    for user in inactive_users:
        if not ScheduledDeletion.objects.filter(user=user, deletion_type='inactive_user', cancelled=False).exists():
            ScheduledDeletion.objects.create(
                user=user,
                deletion_type='inactive_user',
                scheduled_for=now() + timedelta(days=20)
            )
            token = default_token_generator.make_token(user)
            reactivation_url = f"{settings.FRONTEND_URL}/reactivate-account/?token={token}&user_id={user.id}"
            send_inactive_user_email.apply_async(
                args=[user.id, user.email, reactivation_url],
                eta=now() + timedelta(days=3)
            )
    return "Inactive user deletions processed successfully."