# Generated by Django 5.0.6 on 2025-01-21 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0030_alter_pages_token_id_alter_user_token_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pages',
            name='token_id',
            field=models.CharField(default='GklrwTWmPM', max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='Token_ID',
            field=models.CharField(default='Z7IaeI0N8R', max_length=12),
        ),
    ]
