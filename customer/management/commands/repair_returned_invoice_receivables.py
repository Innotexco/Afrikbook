"""Zero AR for cancelled/returned invoices.

Preview first:

    python manage.py repair_returned_invoice_receivables --dry-run
    python manage.py repair_returned_invoice_receivables --db=afrikbook_2952 --dry-run
    python manage.py repair_returned_invoice_receivables --db=afrikbook_2952
"""
from django.core.management.base import BaseCommand, CommandError

from customer.functions.generalFunction import repair_returned_invoice_receivables
from main.db_router import add_db_connection
from Stockin.models import company_table


class Command(BaseCommand):
    help = (
        "Post reversing AR rows so cancelled/returned invoices net to zero. "
        "Receivables then matches Customer Ledger, which omits those invoices."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print planned changes; write nothing.',
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
            default=30,
            help='How many invoices to print per database (default 30).',
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

            try:
                result = repair_returned_invoice_receivables(name, dry_run=dry_run)
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f'[{name}] failed: {exc}'))
                continue

            self.stdout.write('')
            self.stdout.write(self.style.NOTICE(f'[{name}]'))
            self.stdout.write(f'  Returned invoices to zero: {result["changed"]}')
            if not dry_run:
                self.stdout.write(f'  Rewrote {result["recomputed"]} running-balance field(s)')

            for row in result['invoices'][:limit]:
                self.stdout.write(
                    '    {invoiceID} {customer_name} net {net_before} -> {net_after}'.format(**row)
                )
                for action in row['actions']:
                    self.stdout.write(
                        f'      create {action["type"]} {action["amount"]} '
                        f'token={action["token_id"]}'
                    )
            extra = result['changed'] - min(result['changed'], limit)
            if extra > 0:
                self.stdout.write(f'    … {extra} more')

        self.stdout.write('')
        if dry_run:
            self.stdout.write(self.style.SUCCESS(
                'Dry run only. Re-run without --dry-run to write and recompute.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS('Repair finished.'))
