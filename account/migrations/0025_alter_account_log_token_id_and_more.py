# Generated by Django 5.0.6 on 2024-12-18 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0024_alter_account_log_token_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account_log',
            name='token_id',
            field=models.CharField(default='3475158', max_length=255),
        ),
        migrations.AlterField(
            model_name='account_log',
            name='transactionId',
            field=models.CharField(default='hY93i7IO9J', max_length=255),
        ),
        migrations.AlterField(
            model_name='chart_of_account',
            name='token_id',
            field=models.CharField(default='mKFQ56VeiC', max_length=255),
        ),
        migrations.AlterField(
            model_name='transfer_account',
            name='token_id',
            field=models.CharField(blank=True, default='t0uVsWPLlK', max_length=12),
        ),
    ]
