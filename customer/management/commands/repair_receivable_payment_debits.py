"""One-time repair for Aged Receivable payment-echo Debits.

Does not run on page load. Preview first:

    python manage.py repair_receivable_payment_debits --dry-run
    python manage.py repair_receivable_payment_debits
    python manage.py repair_receivable_payment_debits --db=company_db_name
"""
from django.core.management.base import BaseCommand, CommandError

from customer.functions.generalFunction import repair_spurious_payment_debits
from main.db_router import add_db_connection
from Stockin.models import company_table


class Command(BaseCommand):
    help = (
        "Delete Debit receivable rows posted at payment/discount time "
        "(description starts with 'Payment Received' or 'Discount Allowed'), "
        "then recompute every customer's running balance in date/id order."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='List rows that would be deleted; write nothing.',
        )
        parser.add_argument(
            '--db',
            dest='db_name',
            default=None,
            help='Repair one company database. Default: every company.',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='How many candidate rows to print per database (default 20).',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        db_name = options['db_name']
        limit = options['limit']

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

            result = repair_spurious_payment_debits(name, dry_run=dry_run)
            deleted = result['would_delete'] if dry_run else result['deleted']
            self.stdout.write('')
            self.stdout.write(self.style.NOTICE(f'[{name}]'))
            if dry_run:
                self.stdout.write(f'  Would delete {deleted} payment/discount Debit row(s)')
            else:
                self.stdout.write(f'  Deleted {deleted} payment/discount Debit row(s)')
                self.stdout.write(f'  Rewrote {result["recomputed"]} running-balance field(s)')

            for row in result['rows'][:limit]:
                self.stdout.write(
                    '    #{id} {date} {customer_id} {description} amount={amount}'.format(**row)
                )
            extra = deleted - min(deleted, limit)
            if extra > 0:
                self.stdout.write(f'    … {extra} more')

        self.stdout.write('')
        if dry_run:
            self.stdout.write(self.style.SUCCESS(
                'Dry run only. Re-run without --dry-run to delete and recompute.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS('Repair finished.'))
