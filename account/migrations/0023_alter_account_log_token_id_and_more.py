# Generated by Django 5.0.6 on 2024-12-18 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0022_alter_account_log_token_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account_log',
            name='token_id',
            field=models.CharField(default='7609426', max_length=255),
        ),
        migrations.AlterField(
            model_name='account_log',
            name='transactionId',
            field=models.CharField(default='i0zY9VGeJf', max_length=255),
        ),
        migrations.AlterField(
            model_name='chart_of_account',
            name='token_id',
            field=models.CharField(default='eS3B2Kx312', max_length=255),
        ),
        migrations.AlterField(
            model_name='transfer_account',
            name='token_id',
            field=models.CharField(blank=True, default='CfT3GozhSf', max_length=12),
        ),
    ]
