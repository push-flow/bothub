# Generated by Django 2.0.6 on 2018-10-03 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0024_repositoryupdate_use_language_model_featurizer'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='use_competing_intents',
            field=models.BooleanField(default=False, help_text='When using competing intents the confidence of the prediction is distributed in all the intents.', verbose_name='Use competing intents'),
        ),
        migrations.AddField(
            model_name='repositoryupdate',
            name='use_competing_intents',
            field=models.BooleanField(default=False),
        ),
    ]
