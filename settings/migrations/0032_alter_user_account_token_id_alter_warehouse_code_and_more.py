# Generated by Django 5.0.6 on 2025-01-21 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0031_alter_user_account_token_id_alter_warehouse_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_account',
            name='token_ID',
            field=models.CharField(default='lk54RtsWXs', max_length=12),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='code',
            field=models.CharField(default='7906453', max_length=255),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='token_id',
            field=models.CharField(default='dGZlXs8ayT', max_length=255),
        ),
    ]
