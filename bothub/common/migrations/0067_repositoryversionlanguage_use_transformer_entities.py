# Generated by Django 2.2.12 on 2020-06-29 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("common", "0066_repository_use_transformer_entities")]

    operations = [
        migrations.AddField(
            model_name="repositoryversionlanguage",
            name="use_transformer_entities",
            field=models.BooleanField(default=False),
        )
    ]
