# Generated manually — increase genby to hold full customer names

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0043_alter_sales_order_order_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sales_quote',
            name='genby',
            field=models.CharField(max_length=225),
        ),
    ]
