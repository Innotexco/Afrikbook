# Generated by Django 5.0.6 on 2025-01-20 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0029_alter_user_account_token_id_alter_warehouse_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_account',
            name='token_ID',
            field=models.CharField(default='QX1Y9MbcS8', max_length=12),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='code',
            field=models.CharField(default='1396213', max_length=255),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='token_id',
            field=models.CharField(default='xiu1Ib3tNv', max_length=255),
        ),
    ]
