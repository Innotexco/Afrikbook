# Generated by Django 5.0.6 on 2025-01-21 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0033_alter_sales_order_order_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sales_order',
            name='order_ID',
            field=models.CharField(blank=True, default='2459412', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='sales_quote',
            name='quote_ID',
            field=models.CharField(blank=True, default='6806959', max_length=50, null=True),
        ),
    ]
