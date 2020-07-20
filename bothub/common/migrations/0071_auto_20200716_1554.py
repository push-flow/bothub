# Generated by Django 2.2.12 on 2020-07-16 18:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0006_auto_20200716_1554"),
        ("common", "0070_auto_20200714_1206"),
    ]

    operations = [
        migrations.CreateModel(
            name="Organization",
            fields=[
                (
                    "description",
                    models.TextField(blank=True, verbose_name="description"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "repository_owner",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        related_name="organization_owner",
                        serialize=False,
                        to="authentication.RepositoryOwner",
                    ),
                ),
            ],
            options={"verbose_name": "repository organization"},
            bases=("authentication.repositoryowner",),
        ),
        migrations.AlterField(
            model_name="repository",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="repositories",
                to="authentication.RepositoryOwner",
            ),
        ),
        migrations.AlterField(
            model_name="repositoryauthorization",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="authentication.RepositoryOwner",
            ),
        ),
        migrations.AlterField(
            model_name="repositorynlplog",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="authentication.RepositoryOwner",
            ),
        ),
        migrations.AlterField(
            model_name="repositoryversion",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="authentication.RepositoryOwner",
            ),
        ),
        migrations.AlterField(
            model_name="repositoryvote",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="repository_votes",
                to="authentication.RepositoryOwner",
            ),
        ),
    ]
