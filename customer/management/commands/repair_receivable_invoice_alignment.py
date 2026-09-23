"""Align receivable ledger totals with invoice amount_expected / amount_paid.

Preview first:

    python manage.py repair_receivable_invoice_alignment --dry-run
    python manage.py repair_receivable_invoice_alignment --db=afrikbook_2952 --dry-run
    python manage.py repair_receivable_invoice_alignment --db=afrikbook_2952
"""
from django.core.management.base import BaseCommand, CommandError

from customer.functions.generalFunction import repair_receivable_invoice_alignment
from main.db_router import add_db_connection
from Stockin.models import company_table


class Command(BaseCommand):
    help = (
        "Rewrite sale-time receivable Debit/Credit amounts so each invoice's "
        "AR outstanding matches amount_expected - amount_paid. Later "
        "'Payment Received' / 'Discount Allowed' credits are kept."
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
                result = repair_receivable_invoice_alignment(name, dry_run=dry_run)
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f'[{name}] failed: {exc}'))
                continue

            self.stdout.write('')
            self.stdout.write(self.style.NOTICE(f'[{name}]'))
            self.stdout.write(f'  Invoices to change: {result["changed"]}')
            if not dry_run:
                self.stdout.write(f'  Rewrote {result["recomputed"]} running-balance field(s)')

            for row in result['invoices'][:limit]:
                self.stdout.write(
                    '    {invoiceID} {customer_name} expected={expected} paid={paid} '
                    'AR {ar_debit_before}/{ar_credit_before} -> {ar_debit_after}/{ar_credit_after}'.format(**row)
                )
                for action in row['actions']:
                    op = action.get('op')
                    if op == 'update':
                        self.stdout.write(
                            f'      update #{action["id"]} {action["type"]} '
                            f'{action["from"]} -> {action["to"]}'
                        )
                    elif op == 'delete':
                        self.stdout.write(
                            f'      delete #{action["id"]} {action["type"]} {action["amount"]}'
                        )
                    elif op == 'create':
                        self.stdout.write(
                            f'      create {action["type"]} {action["amount"]}'
                        )
                    elif op == 'sync_lines':
                        self.stdout.write(
                            f'      sync {action["line_count"]} line(s) amount_paid -> {action["to"]}'
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
