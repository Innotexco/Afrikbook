# Generated by Django 5.0.6 on 2024-12-17 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_alter_pages_token_id_alter_user_token_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pages',
            name='token_id',
            field=models.CharField(default='ADEUZUEwF7', max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='Token_ID',
            field=models.CharField(default='omGOczc3Ct', max_length=12),
        ),
    ]
