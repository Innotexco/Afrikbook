# Generated by Django 5.0.6 on 2025-01-21 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Stock', '0031_alter_category_token_id_alter_item_token_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='token_id',
            field=models.CharField(blank=True, default='iCDLOeEVBc', max_length=25),
        ),
        migrations.AlterField(
            model_name='item',
            name='token_id',
            field=models.CharField(default='W0rfLsPDGc', max_length=255),
        ),
    ]
