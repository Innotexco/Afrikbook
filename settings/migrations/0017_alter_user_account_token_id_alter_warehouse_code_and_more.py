# Generated by Django 5.0.6 on 2024-12-17 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0016_alter_user_account_token_id_alter_warehouse_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_account',
            name='token_ID',
            field=models.CharField(default='VY8bQdd2N3', max_length=12),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='code',
            field=models.CharField(default='5828689', max_length=255),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='token_id',
            field=models.CharField(default='d46TEABDBM', max_length=255),
        ),
    ]
