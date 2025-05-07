from backend.utils.default_scheduled_time import default_scheduled_time
from backend.utils.email import send_email
from backend.utils.deletions import schedule_deletion, cancel_user_scheduled_deletion, process_scheduled_user_deletions
from authentication.models import ScheduledDeletion
# from social_django.models import UserSocialAuth
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def schedule_user_deletion(request):
    user = request.user

    if ScheduledDeletion.objects.filter(user=user, deletion_type='user', cancelled=False).exists():
        return Response({'success': False, 'error': 'Deletion already scheduled'}, status=400)
    
    schedule_deletion(user, deletion_type='user', days=7)

    # Send email to user
    send_email(
        subject="Account Deletion Scheduled",
        message="Your account is scheduled for deletion in 7 days. If you wish to cancel this deletion, please contact support.",
        recipient_list=[user.email],
    )

    return Response({'success': True, 'message': 'Deletion scheduled successfully for 7 days from now'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def schedule_inactive_user_deletion(request):
    user = request.user

    if user.is_active:
        return Response({'success': False, 'error': 'User is active'}, status=400)
    
    if ScheduledDeletion.objects.filter(user=user, deletion_type='inactive_user').exists():
        return Response({'success': False, 'error': 'Deletion already scheduled'}, status=400)
    
    schedule_deletion(user, deletion_type='inactive_user', days=20)

    # Send email to user
    send_email(
        subject="Inactive Account Scheduled for Deletion",
        message="Your account is scheduled for deletion in 7 days due to inactivity. If you wish to keep your account, please contact support or use the cancel deletion option.",
        recipient_list=[user.email],
    )

    return Response({'success': True, 'message': 'Deletion scheduled successfully for 7 days from now'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def schedule_social_auth_deletion(request):
    user = request.user
    provider = request.data.get('provider')

    if not provider:
        return Response({'success': False, 'error': 'Provider is required'}, status=400)

    try:
        social_auth = UserSocialAuth.objects.get(user=user, provider=provider)

        if ScheduledDeletion.objects.filter(social_auth=social_auth, deletion_type='social_auth', cancelled=False).exists():
            return Response({'success': False, 'error': 'Deletion already scheduled'}, status=400)
        
        schedule_deletion(user, deletion_type='social_auth', days=7)

        send_email(
            subject="Social Auth Account Deletion Scheduled",
            message=f"Your {provider} account is scheduled for deletion in 7 days. If you wish to cancel this deletion, please contact support or use the cancel deletion option.",
            recipient_list=[user.email],
        )
        
        return Response({'success': True, 'message': 'Deletion scheduled successfully for 7 days from now'})
    
    except UserSocialAuth.DoesNotExist:
        return Response({'success': False, 'error': f'{provider} account not linked'}, status=404)

def cancel_user_scheduled_deletion(user):
    """
    Cancel a scheduled deletion for a user.
    
    Args:
        user: The user to cancel deletion for.
    
    Returns:
        True if a deletion was canceled, False otherwise.
    """
    scheduled_deletion = ScheduledDeletion.objects.filter(user=user, cancelled=False)

    if scheduled_deletion.exists():
        send_email(
            subject="Account Deletion Canceled",
            message="Your account deletion has been cancelled successfully.",
            recipient_list=[user.email],
        )
        
        for deletion in scheduled_deletion:
            deletion.cancelled = True
            deletion.save()
        return True
    return False

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_scheduled_deletion(request):
    user = request.user

    # Attempt to cancel the scheduled deletion
    deletion_canceled = cancel_user_scheduled_deletion(user)

    if deletion_canceled:
        # Send email notification to the user
        try:
            send_email(
                subject="Account Deletion Canceled",
                message="Your account deletion has been cancelled successfully.",
                recipient_list=[user.email],
            )
        except Exception as e:
            # Log the email failure (optional)
            print(f"Failed to send email to {user.email}: {str(e)}")

        return Response({'success': True, 'message': 'Deletion cancelled successfully'}, status=200)
    else:
        return Response({'success': False, 'error': 'No scheduled deletion found'}, status=400)