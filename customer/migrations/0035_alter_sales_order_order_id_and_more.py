# Generated by Django 5.0.6 on 2025-01-21 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0034_alter_sales_order_order_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sales_order',
            name='order_ID',
            field=models.CharField(blank=True, default='4726018', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='sales_quote',
            name='quote_ID',
            field=models.CharField(blank=True, default='8321503', max_length=50, null=True),
        ),
    ]
