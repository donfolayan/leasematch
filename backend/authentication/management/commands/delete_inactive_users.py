from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta
from authentication.models import CustomUser

class Command(BaseCommand):
    help = 'Delete users who have not verified their accounts within 24 hours'

    def handle(self, *args, **kwargs):
        cutoff_time = now() - timedelta(hours=24)
        inactive_users = CustomUser.objects.filter(is_active=False, date_joined__lt=cutoff_time)
        count = inactive_users.count()
        inactive_users.delete()
        self.stdout.write(f'{count} inactive users deleted.')