from django.core.management.base import BaseCommand
from django.utils import timezone
from whatsapp_bot.models import Comedian, VotingSession


class Command(BaseCommand):
    help = 'Set up initial data for the comedian voting bot'

    def handle(self, *args, **options):
        # Create comedians
        comedians_data = ['Eliud', 'Nanga', 'Brother K', 'Ndaro', 'Steve Mweusi']
        
        for name in comedians_data:
            comedian, created = Comedian.objects.get_or_create(name=name)
            if created:
                self.stdout.write(f'Created comedian: {name}')
            else:
                self.stdout.write(f'Comedian already exists: {name}')
        
        # Create voting session
        session, created = VotingSession.objects.get_or_create(
            name="Comedian Bora wa Mwezi - October 2024",
            defaults={
                'end_date': timezone.now() + timezone.timedelta(days=30),
                'winner_announcement_date': timezone.now() + timezone.timedelta(days=35)
            }
        )
        
        if created:
            self.stdout.write(f'Created voting session: {session.name}')
        else:
            self.stdout.write(f'Voting session already exists: {session.name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up initial data!')
        )
