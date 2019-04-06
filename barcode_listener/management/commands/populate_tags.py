from django.core.management.base import BaseCommand
from taggit.models import Tag


class Command(BaseCommand):
    help = 'Populate all the tags'

    def handle(self, *args, **options):
        tags = ["six_months_life", "two_weeks_life", "one_weeks_life", "frozen", "remaining_100", "remaining_75",
                "remaining_50", "remaining_25", "remaining_10", "remaining_0", "delete_stock", 'reset_stack']
        for tag in tags:
            Tag.objects.get_or_create(name=tag)
            self.stdout.write(self.style.SUCCESS('Successfully created tags'))
