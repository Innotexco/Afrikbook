# Generated by Django 5.0.6 on 2024-12-17 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0018_alter_user_account_token_id_alter_warehouse_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_account',
            name='token_ID',
            field=models.CharField(default='FU9oiIFnqb', max_length=12),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='code',
            field=models.CharField(default='5521831', max_length=255),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='token_id',
            field=models.CharField(default='y5cSz0Khyi', max_length=255),
        ),
    ]
