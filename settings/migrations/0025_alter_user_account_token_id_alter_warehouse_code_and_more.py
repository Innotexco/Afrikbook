# Generated by Django 5.0.6 on 2024-12-18 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0024_alter_user_account_token_id_alter_warehouse_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_account',
            name='token_ID',
            field=models.CharField(default='IaTWB4ykHH', max_length=12),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='code',
            field=models.CharField(default='9007276', max_length=255),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='token_id',
            field=models.CharField(default='iS6S6M76AH', max_length=255),
        ),
    ]
