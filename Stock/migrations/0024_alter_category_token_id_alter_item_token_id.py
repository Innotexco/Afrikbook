# Generated by Django 5.0.6 on 2024-12-18 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Stock', '0023_alter_category_token_id_alter_item_token_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='token_id',
            field=models.CharField(blank=True, default='cSayLuFHkV', max_length=25),
        ),
        migrations.AlterField(
            model_name='item',
            name='token_id',
            field=models.CharField(default='AGzieGCXQy', max_length=255),
        ),
    ]
