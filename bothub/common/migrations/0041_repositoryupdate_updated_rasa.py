# Generated by Django 2.1.11 on 2019-11-27 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("common", "0040_repositoryupdate_publish")]

    operations = [
        migrations.AddField(
            model_name="repositoryupdate",
            name="updated_rasa",
            field=models.BooleanField(default=False),
        )
    ]
