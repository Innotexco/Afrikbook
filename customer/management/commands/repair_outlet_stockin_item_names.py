"""Fill empty outlet stock-in item names from the item master.

    python manage.py repair_outlet_stockin_item_names --dry-run
    python manage.py repair_outlet_stockin_item_names --db=afrikbook_2952
"""
from django.core.management.base import BaseCommand, CommandError

from main.db_router import add_db_connection
from Stock.functions.functionHub.functionHub import repair_blank_outlet_stockin_item_names
from Stockin.models import company_table


class Command(BaseCommand):
    help = "Fill blank warehouse and outlet stock-in item names from Item.item_name or item_code."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Count rows that would be filled; write nothing.',
        )
        parser.add_argument(
            '--db',
            dest='db_name',
            default=None,
            help='Repair one company database. Default: every company.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        db_name = options['db_name']

        if db_name:
            db_names = [db_name]
        else:
            db_names = list(
                company_table.objects.exclude(db_name__isnull=True)
                .exclude(db_name='')
                .values_list('db_name', flat=True)
                .distinct()
            )
            if not db_names:
                raise CommandError('No company databases found.')

        mode = 'DRY RUN' if dry_run else 'APPLY'
        self.stdout.write(self.style.WARNING(f'{mode} on {len(db_names)} database(s)'))

        for name in db_names:
            if not add_db_connection(name):
                self.stderr.write(self.style.ERROR(f'Could not connect to {name}'))
                continue
            try:
                count = repair_blank_outlet_stockin_item_names(name, dry_run=dry_run)
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f'[{name}] failed: {exc}'))
                continue
            self.stdout.write(f'[{name}] blank item rows={count}')
