# Generated by Django 5.0.6 on 2024-12-12 11:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Stockin', '0001_initial'),
        ('main', '0010_alter_pages_token_id_alter_user_token_id_billing_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pages',
            name='token_id',
            field=models.CharField(default='4CSfbzlVUH', max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='Token_ID',
            field=models.CharField(default='mo8u15advn', max_length=12),
        ),
       
    ]
