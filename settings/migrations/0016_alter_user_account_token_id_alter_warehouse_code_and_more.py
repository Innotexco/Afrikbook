# Generated by Django 5.0.6 on 2024-12-16 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0015_alter_user_account_token_id_alter_warehouse_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_account',
            name='token_ID',
            field=models.CharField(default='VOWekO6SLb', max_length=12),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='code',
            field=models.CharField(default='0151974', max_length=255),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='token_id',
            field=models.CharField(default='zX2CgbRAiW', max_length=255),
        ),
    ]
