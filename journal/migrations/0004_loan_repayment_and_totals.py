from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0003_loan_installment'),
    ]

    operations = [
        migrations.AddField(
            model_name='loan_account',
            name='interest_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='loan_account',
            name='total_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='loan_installment',
            name='extended_interest_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.CreateModel(
            name='loan_repayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loan_id', models.IntegerField()),
                ('installment_id', models.IntegerField()),
                ('invoice_id', models.CharField(blank=True, max_length=200)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('date', models.DateField()),
                ('source', models.CharField(blank=True, default='aged_receivable', max_length=60)),
                ('payment_method', models.CharField(blank=True, max_length=80)),
                ('Userlogin', models.CharField(blank=True, max_length=60)),
                ('note', models.CharField(blank=True, max_length=250)),
            ],
            options={
                'db_table': 'loan_repayment',
            },
        ),
    ]
