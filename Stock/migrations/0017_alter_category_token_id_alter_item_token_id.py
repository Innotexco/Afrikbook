# Generated by Django 5.0.6 on 2024-12-16 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Stock', '0016_alter_category_token_id_alter_item_token_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='token_id',
            field=models.CharField(blank=True, default='wWe3deqSy0', max_length=25),
        ),
        migrations.AlterField(
            model_name='item',
            name='token_id',
            field=models.CharField(default='M62j7qwn3A', max_length=255),
        ),
    ]
