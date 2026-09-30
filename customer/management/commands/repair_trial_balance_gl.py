"""Rebuild chart balances and series logs as double-entry so Trial Balance balances.

Preview first:

    python manage.py repair_trial_balance_gl --dry-run
    python manage.py repair_trial_balance_gl --db=afrikbook_2952 --dry-run
    python manage.py repair_trial_balance_gl --db=afrikbook_2952
"""
from django.core.management.base import BaseCommand, CommandError

from customer.functions.gl import repair_trial_balance_gl
from main.db_router import add_db_connection
from report.views import compute_trial_balance
from Stockin.models import company_table


class Command(BaseCommand):
    help = (
        "Wipe one-sided series logs, reset chart actual_balance, and replay "
        "sales, returns, receipts, purchases, and loans as double-entry."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print planned replay counts; write nothing.',
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
                result = repair_trial_balance_gl(name, dry_run=dry_run)
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f'[{name}] failed: {exc}'))
                continue

            self.stdout.write('')
            self.stdout.write(self.style.NOTICE(f'[{name}]'))
            self.stdout.write(
                f'  sales={result["sales"]} ({result["sale_total"]})  '
                f'returns={result["returns"]} ({result["return_total"]})  '
                f'paid={result["paid_total"]}'
            )
            self.stdout.write(
                f'  purchases={result["purchases"]} ({result["purchase_total"]})  '
                f'loans={result["loans"]} ({result["loan_total"]})  '
                f'unallocated={result["unallocated"]} ({result["unallocated_total"]})'
            )

            if not dry_run:
                tb = compute_trial_balance(name)
                flag = 'BALANCED' if tb['is_balanced'] else f'OFF by {tb["difference"]}'
                self.stdout.write(
                    f'  Trial Balance live  Dr {tb["debit_total"]}  '
                    f'Cr {tb["credit_total"]}  {flag}'
                )

        self.stdout.write('')
        if dry_run:
            self.stdout.write(self.style.SUCCESS(
                'Dry run only. Re-run without --dry-run to rebuild the GL.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS('GL rebuild finished.'))
