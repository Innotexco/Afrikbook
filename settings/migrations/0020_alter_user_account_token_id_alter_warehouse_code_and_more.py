# Generated by Django 5.0.6 on 2024-12-17 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0019_alter_user_account_token_id_alter_warehouse_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_account',
            name='token_ID',
            field=models.CharField(default='SMBGixJfmE', max_length=12),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='code',
            field=models.CharField(default='8116588', max_length=255),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='token_id',
            field=models.CharField(default='5sAaxXagk5', max_length=255),
        ),
    ]
