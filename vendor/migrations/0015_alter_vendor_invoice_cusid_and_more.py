# Generated by Django 5.0.6 on 2024-12-13 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0014_alter_vendor_invoice_cusid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor_invoice',
            name='cusID',
            field=models.CharField(blank=True, default='7759845', max_length=25),
        ),
        migrations.AlterField(
            model_name='vendor_invoice',
            name='token_id',
            field=models.CharField(blank=True, default='-EXFmRDRgf', max_length=255),
        ),
        migrations.AlterField(
            model_name='vendor_order',
            name='custID',
            field=models.CharField(blank=True, default='jtoNqmPk1W', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_order',
            name='order_ID',
            field=models.CharField(blank=True, default='9456114', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_order',
            name='token_id',
            field=models.CharField(blank=True, default='1725837', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_quote',
            name='custID',
            field=models.CharField(blank=True, default='vXWCGTXZMi', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_quote',
            name='quote_ID',
            field=models.CharField(blank=True, default='9456674', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_quote',
            name='token_id',
            field=models.CharField(blank=True, default='1043648', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_return',
            name='cusID',
            field=models.CharField(blank=True, default='IPSVaVv-3V', max_length=255),
        ),
        migrations.AlterField(
            model_name='vendor_return',
            name='token_id',
            field=models.CharField(blank=True, default='1479259', max_length=25, null=True),
        ),
    ]
