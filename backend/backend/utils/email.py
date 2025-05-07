from django.core.mail import send_mail
from django.conf import settings

def send_email(subject, message, recipient_list):
    """
    Send an email using Django's send_mail function.
    
    Args:
        subject (str): The subject of the email.
        message (str): The body of the email.
        recipient_list (list): A list of recipient email addresses.
    """
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
    )