# Generated by Django 5.0.6 on 2024-12-17 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0019_alter_sales_order_order_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sales_order',
            name='order_ID',
            field=models.CharField(blank=True, default='4740287', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='sales_quote',
            name='quote_ID',
            field=models.CharField(blank=True, default='9619624', max_length=50, null=True),
        ),
    ]
