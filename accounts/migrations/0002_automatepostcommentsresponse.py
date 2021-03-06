# Generated by Django 3.2.4 on 2021-07-05 21:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AutomatePostCommentsResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post', models.CharField(max_length=255, verbose_name='post id')),
                ('response', models.CharField(max_length=500)),
                ('response_privetly', models.CharField(blank=True, max_length=1000, null=True)),
                ('name', models.CharField(max_length=255, verbose_name='automate name')),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.facebookpage')),
            ],
        ),
    ]
