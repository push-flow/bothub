# Generated by Django 2.2.12 on 2020-06-16 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0065_auto_20200616_1007'),
    ]

    operations = [
        migrations.AddField(
            model_name='repositoryqueuetask',
            name='ml_units',
            field=models.FloatField(default=0, verbose_name='Machine Learning Units AiPlatform'),
        ),
    ]
