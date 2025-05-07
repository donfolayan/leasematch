from datetime import datetime, timedelta
from django.utils.timezone import now
from authentication.models import ScheduledDeletion
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from authentication.models import CustomUser, ScheduledDeletion
from backend.utils.default_scheduled_time import default_scheduled_time


def schedule_deletion(user, deletion_type, days=7):
    """
    Schedule a deletion for a user.
    
    Args:
        user: The user to schedule deletion for.
        deletion_type: The type of deletion ('user', 'inactive_user', 'social_auth').
        days: Number of days until deletion (default is 7).
    
    Returns:
        A dictionary with success status and message.
    """
    if ScheduledDeletion.objects.filter(user=user, deletion_type=deletion_type, cancelled=False).exists():
        return {'success': False, 'error': 'Deletion already scheduled'}
    

    ScheduledDeletion.objects.create(
        user=user, 
        deletion_type=deletion_type, 
        scheduled_for=now() + timedelta(days=days)
    )
    return {'success': True, 'message': 'Deletion scheduled sucessfully'}
def cancel_user_scheduled_deletion(user):
    """
    Cancel a scheduled deletion for a user.
    
    Args:
        user: The user to cancel deletion for.
    
    Returns:
        A dictionary with success status and message.
    """
    scheduled_deletion = ScheduledDeletion.objects.filter(user=user, cancelled=False)

    if scheduled_deletion.exists():
        for deletion in scheduled_deletion:
            deletion.cancelled = True
            deletion.save()
        return {'success': True, 'message': 'Deletion cancelled successfully'}
    else:
        return {'success': False, 'error': 'No scheduled deletion found'}
    
def process_scheduled_user_deletions():
    """
    Process scheduled deletions that are due.
    
    Returns:
        A list of messages indicating the status of each deletion.
    """
    messages = []
    scheduled_deletions = ScheduledDeletion.objects.filter(scheduled_for__lte=now, cancelled=False)
    
    for deletion in scheduled_deletions:
        try:
            if deletion.deletion_type == 'user':
                deletion.user.delete()
                messages.append(f"User {deletion.user.email} deleted successfully.")
            elif deletion.deletion_type == 'social_auth':
                social_auth = deletion.user.social_auth.all()
                for social_auth in social_auth:
                    social_auth.delete()
                    messages.append(f"Social auth account for {deletion.user.email} deleted successfully.")
            elif deletion.deletion_type == 'inactive_user':
                deletion.user.delete()
                messages.append(f"Inactive user {deletion.user.email} deleted successfully.")
            
            deletion.delete()  # Remove the scheduled deletion record
        except Exception as e:
            messages.append(f"Error processing deletion for {deletion.user.email}: {str(e)}")
    return messages