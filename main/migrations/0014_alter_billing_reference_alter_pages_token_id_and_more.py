# Generated by Django 5.0.6 on 2024-12-13 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_alter_pages_token_id_alter_user_token_id_billing_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billing',
            name='reference',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='pages',
            name='token_id',
            field=models.CharField(default='r9fJw3IG6U', max_length=255),
        ),
        migrations.AlterField(
            model_name='subhistory',
            name='reference',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='Token_ID',
            field=models.CharField(default='2BnEJooIBs', max_length=12),
        ),
    ]
