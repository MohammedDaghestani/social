# Generated by Django 3.2.4 on 2021-08-08 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20210808_1428'),
    ]

    operations = [
        migrations.AlterField(
            model_name='automatepostcommentsresponse',
            name='words',
            field=models.JSONField(blank=True, null=True),
        ),
    ]