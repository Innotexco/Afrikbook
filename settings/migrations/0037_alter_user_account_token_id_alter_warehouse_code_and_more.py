# Generated by Django 5.0.6 on 2025-01-24 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0036_alter_user_account_token_id_alter_warehouse_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_account',
            name='token_ID',
            field=models.CharField(default='cEWHbWLjjK', max_length=12),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='code',
            field=models.CharField(default='6932450', max_length=255),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='token_id',
            field=models.CharField(default='E32R9hGtZL', max_length=255),
        ),
    ]
