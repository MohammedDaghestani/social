# Generated by Django 3.2.4 on 2021-08-16 11:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webhooks', '0007_insights_data'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Insights',
        ),
    ]