from django.core.management.base import BaseCommand
from authentication.models import CustomUser

class Command(BaseCommand):
    help = 'Delete all users from the database'

    def handle(self, *args, **kwargs):
        CustomUser.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All users have been deleted.'))