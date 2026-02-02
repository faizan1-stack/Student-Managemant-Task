from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule

class Command(BaseCommand):
    help = 'Setup Celery Beat periodic tasks'

    def handle(self, *args, **options):
       
        interval_1min, _ = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.MINUTES
        )
        
        PeriodicTask.objects.update_or_create(
            name='discard_expired',
            defaults={
                'task': 'Teacher.tasks.discard_expired_enrollments',
                'interval': interval_1min,
                'enabled': True,
            }
        )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created periodic tasks')
        )
