# Generated by Django 5.0.6 on 2024-12-18 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_alter_pages_token_id_alter_user_token_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pages',
            name='token_id',
            field=models.CharField(default='EmSXhw6qN5', max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='Token_ID',
            field=models.CharField(default='duInzyNzJa', max_length=12),
        ),
    ]
