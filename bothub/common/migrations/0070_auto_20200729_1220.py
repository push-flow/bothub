# Generated by Django 2.2.12 on 2020-07-29 15:20

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0006_auto_20200729_1220"),
        ("common", "0069_auto_20200703_1437"),
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
                ("verificated", models.BooleanField(default=False)),
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
            name="algorithm",
            field=models.CharField(
                choices=[
                    (
                        "neural_network_internal",
                        "Neural Network with internal vocabulary",
                    ),
                    (
                        "neural_network_external",
                        "Neural Network with external vocabulary (BETA)",
                    ),
                    (
                        "transformer_network_diet",
                        "Transformer Neural Network with internal vocabulary",
                    ),
                    (
                        "transformer_network_diet_word_embedding",
                        "Transformer Neural Network with word embedding external vocabulary",
                    ),
                    (
                        "transformer_network_diet_bert",
                        "Transformer Neural Network with BERT word embedding",
                    ),
                ],
                default="transformer_network_diet",
                max_length=50,
                verbose_name="algorithm",
            ),
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
            model_name="repositoryversionlanguage",
            name="algorithm",
            field=models.CharField(
                choices=[
                    (
                        "neural_network_internal",
                        "Neural Network with internal vocabulary",
                    ),
                    (
                        "neural_network_external",
                        "Neural Network with external vocabulary (BETA)",
                    ),
                    (
                        "transformer_network_diet",
                        "Transformer Neural Network with internal vocabulary",
                    ),
                    (
                        "transformer_network_diet_word_embedding",
                        "Transformer Neural Network with word embedding external vocabulary",
                    ),
                    (
                        "transformer_network_diet_bert",
                        "Transformer Neural Network with BERT word embedding",
                    ),
                ],
                default="transformer_network_diet",
                max_length=50,
                verbose_name="algorithm",
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
        migrations.CreateModel(
            name="OrganizationAuthorization",
            fields=[
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        verbose_name="UUID",
                    ),
                ),
                (
                    "role",
                    models.PositiveIntegerField(
                        choices=[
                            (0, "not set"),
                            (1, "user"),
                            (2, "contributor"),
                            (3, "admin"),
                            (4, "translate"),
                        ],
                        default=0,
                        verbose_name="role",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="organization_authorizations",
                        to="common.Organization",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="organization_user_authorization",
                        to="authentication.RepositoryOwner",
                    ),
                ),
            ],
            options={
                "verbose_name": "organization authorization",
                "verbose_name_plural": "organization authorizations",
                "unique_together": {("user", "organization")},
            },
        ),
    ]