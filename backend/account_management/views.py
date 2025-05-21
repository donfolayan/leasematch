from backend.utils.email import send_email
from backend.utils.deletions import schedule_deletion, cancel_user_scheduled_deletion, process_scheduled_user_deletions
from authentication.models import ScheduledDeletion
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def schedule_user_deletion(request):
    user = request.user

    if ScheduledDeletion.objects.filter(user=user, deletion_type='user', cancelled=False).exists():
        return Response({'success': False, 'error': 'Deletion already scheduled'}, status=400)
    
    schedule_deletion(user, deletion_type='user', days=7)

    #Send email to user
    send_email(
        subject="Account Deletion Scheduled",
        message="Your account is scheduled for deletion in 7 days. If you wish to cancel this deletion, please contact support.",
        recipient_list=[user.email],
    )

    return Response({'success': True, 'message': 'Deletion scheduled successfully for 7 days from now'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_scheduled_deletion(request):
    """
    API view to cancel a scheduled deletion for the authenticated user.

    Args:
        request: The HTTP request object containing the user information.

    Returns:
        Response: A JSON response indicating the success or failure of the operation.
    """
    user = request.user
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
            # Log the email failure
            logger.error(f"Failed to send email to {user.email}: {str(e)}")

        return Response({'success': True, 'message': 'Deletion cancelled successfully'}, status=200)
    else:
        return Response({'success': False, 'error': 'No scheduled deletion found'}, status=400)
    
@api_view(['POST'])
@permission_classes([IsAdminUser])
def process_scheduled_deletions(request):
    """
    API view to process scheduled deletions.

    Args:
        request: The HTTP request object.

    Returns:
        Response: A JSON response indicating the success or failure of the operation.
    """
    try:
        process_scheduled_user_deletions()
        logger.info("Admin %s processed scheduled deletions", request.user.email)
        return Response({'success': True,
                         'message': 'Scheduled deletions processed.'}, status=200)
    except Exception as e:
        logger.error("Error processing scheduled deletions: %s", str(e))
        return Response({'success': False,
                         'error': str(e)}, 
                         status=500)
