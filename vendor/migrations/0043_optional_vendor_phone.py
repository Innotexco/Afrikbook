from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0042_alter_vendor_invoice_cusid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor_table',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
    ]
