# Generated by Django 5.0.6 on 2024-12-11 10:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Stockin', '0001_initial'),
        ('main', '0009_alter_pages_token_id_alter_user_token_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pages',
            name='token_id',
            field=models.CharField(default='oqOBGD13LM', max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='Token_ID',
            field=models.CharField(default='yLpauQsr5d', max_length=12),
        ),
        
    ]
