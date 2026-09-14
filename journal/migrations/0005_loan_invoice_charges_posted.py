from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0004_loan_repayment_and_totals'),
    ]

    operations = [
        migrations.AddField(
            model_name='loan_account',
            name='invoice_charges_posted',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, null=True),
        ),
    ]
