# Generated by Django 5.0.6 on 2024-12-17 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0020_alter_vendor_invoice_cusid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor_invoice',
            name='cusID',
            field=models.CharField(blank=True, default='3369456', max_length=25),
        ),
        migrations.AlterField(
            model_name='vendor_invoice',
            name='token_id',
            field=models.CharField(blank=True, default='yYKOck9dnG', max_length=255),
        ),
        migrations.AlterField(
            model_name='vendor_order',
            name='custID',
            field=models.CharField(blank=True, default='AM2O8yL3RM', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_order',
            name='order_ID',
            field=models.CharField(blank=True, default='5269159', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_order',
            name='token_id',
            field=models.CharField(blank=True, default='4096776', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_quote',
            name='custID',
            field=models.CharField(blank=True, default='0TlYH6n222', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_quote',
            name='quote_ID',
            field=models.CharField(blank=True, default='1194584', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_quote',
            name='token_id',
            field=models.CharField(blank=True, default='6153596', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_return',
            name='cusID',
            field=models.CharField(blank=True, default='g8qCb7OtOC', max_length=255),
        ),
        migrations.AlterField(
            model_name='vendor_return',
            name='token_id',
            field=models.CharField(blank=True, default='2551630', max_length=25, null=True),
        ),
    ]
