from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0002_optional_narration_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='loan_installment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loan_id', models.IntegerField()),
                ('transaction_id', models.CharField(max_length=200)),
                ('month_number', models.PositiveSmallIntegerField()),
                ('due_date', models.DateField()),
                ('principal_portion', models.DecimalField(decimal_places=2, max_digits=12)),
                ('interest_portion', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('expected_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('amount_paid', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
            ],
            options={
                'db_table': 'loan_installment',
            },
        ),
    ]
