# Generated by Django 5.0.6 on 2024-12-09 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_alter_account_log_token_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account_log',
            name='token_id',
            field=models.CharField(default='6049772', max_length=255),
        ),
        migrations.AlterField(
            model_name='account_log',
            name='transactionId',
            field=models.CharField(default='QbF8YoLbpp', max_length=255),
        ),
        migrations.AlterField(
            model_name='chart_of_account',
            name='token_id',
            field=models.CharField(default='9a9XZkPSJP', max_length=255),
        ),
        migrations.AlterField(
            model_name='transfer_account',
            name='token_id',
            field=models.CharField(blank=True, default='1dpuScPLCt', max_length=12),
        ),
    ]
