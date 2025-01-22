# Generated by Django 5.0.6 on 2024-12-18 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0027_alter_vendor_invoice_cusid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor_invoice',
            name='cusID',
            field=models.CharField(blank=True, default='0963012', max_length=25),
        ),
        migrations.AlterField(
            model_name='vendor_invoice',
            name='token_id',
            field=models.CharField(blank=True, default='uoWnvQbsBO', max_length=255),
        ),
        migrations.AlterField(
            model_name='vendor_order',
            name='custID',
            field=models.CharField(blank=True, default='NGzvIzCRLv', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_order',
            name='order_ID',
            field=models.CharField(blank=True, default='8826635', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_order',
            name='token_id',
            field=models.CharField(blank=True, default='6118907', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_quote',
            name='custID',
            field=models.CharField(blank=True, default='swmXKcvEqc', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_quote',
            name='quote_ID',
            field=models.CharField(blank=True, default='2842818', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_quote',
            name='token_id',
            field=models.CharField(blank=True, default='6916308', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_return',
            name='cusID',
            field=models.CharField(blank=True, default='OkRwtOO5Py', max_length=255),
        ),
        migrations.AlterField(
            model_name='vendor_return',
            name='token_id',
            field=models.CharField(blank=True, default='9784153', max_length=25, null=True),
        ),
    ]
