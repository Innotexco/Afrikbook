# Generated by Django 5.0.6 on 2024-12-09 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0007_alter_vendor_invoice_cusid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor_invoice',
            name='cusID',
            field=models.CharField(blank=True, default='0235966', max_length=25),
        ),
        migrations.AlterField(
            model_name='vendor_invoice',
            name='token_id',
            field=models.CharField(blank=True, default='N7f5U4wCES', max_length=255),
        ),
        migrations.AlterField(
            model_name='vendor_order',
            name='custID',
            field=models.CharField(blank=True, default='wS7RJEKRsv', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_order',
            name='order_ID',
            field=models.CharField(blank=True, default='0438880', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_order',
            name='token_id',
            field=models.CharField(blank=True, default='7611563', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_quote',
            name='custID',
            field=models.CharField(blank=True, default='o-cyHnIA7i', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_quote',
            name='quote_ID',
            field=models.CharField(blank=True, default='5454149', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_quote',
            name='token_id',
            field=models.CharField(blank=True, default='2230534', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_return',
            name='cusID',
            field=models.CharField(blank=True, default='_4-Bs-hNDE', max_length=255),
        ),
        migrations.AlterField(
            model_name='vendor_return',
            name='token_id',
            field=models.CharField(blank=True, default='0142375', max_length=25, null=True),
        ),
    ]
