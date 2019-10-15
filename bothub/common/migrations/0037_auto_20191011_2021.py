# Generated by Django 2.1.11 on 2019-10-11 20:21

import django.utils.timezone
from django.db import migrations, models
from django.conf import settings
from bothub.utils import send_bot_data_file_aws
from bothub.common.models import RepositoryUpdate
from bothub.common.models import Repository


def updateRepository(apps, schema_editor):
    for update in RepositoryUpdate.objects.all().filter(trained_at__isnull=False):
        repository = Repository.objects.get(uuid=update.repository.uuid)
        repository.total_updates += 1
        repository.save()


def update_repository(apps, schema_editor):
    if settings.AWS_SEND:
        for update in RepositoryUpdate.objects.all().exclude(bot_data__exact=""):
            repository_update = RepositoryUpdate.objects.get(pk=update.pk)
            bot_data = send_bot_data_file_aws(update.pk, update.bot_data)
            repository_update.bot_data = bot_data
            repository_update.save(update_fields=["bot_data"])
            print("Updating bot_data repository_update {}".format(str(update.pk)))


class Migration(migrations.Migration):

    dependencies = [("common", "0031_auto_20190502_1732")]

    operations = [
        migrations.RemoveField(model_name="repositoryvote", name="vote"),
        migrations.AddField(
            model_name="repository",
            name="nlp_server",
            field=models.URLField(blank=True, null=True, verbose_name="Base URL NLP"),
        ),
        migrations.AddField(
            model_name="repository",
            name="total_updates",
            field=models.IntegerField(default=0, verbose_name="total updates"),
        ),
        migrations.RunPython(updateRepository),
        migrations.AddField(
            model_name="repositoryvote",
            name="created",
            field=models.DateTimeField(
                default=django.utils.timezone.now, editable=False
            ),
        ),
        migrations.RunPython(update_repository),
        migrations.AlterField(
            model_name="repositoryupdate",
            name="bot_data",
            field=models.TextField(blank=True, verbose_name="bot data"),
        ),
    ]
