# Generated by Django 5.0.6 on 2025-01-24 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0036_alter_pages_token_id_alter_user_token_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pages',
            name='token_id',
            field=models.CharField(default='J9eyBpE0y3', max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='Token_ID',
            field=models.CharField(default='aNzICHyqPs', max_length=12),
        ),
    ]
