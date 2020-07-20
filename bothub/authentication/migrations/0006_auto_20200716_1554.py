# Generated by Django 2.2.12 on 2020-07-16 18:54

import bothub.authentication.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re


class Migration(migrations.Migration):

    dependencies = [("authentication", "0005_auto_20180620_2059")]

    operations = [
        migrations.CreateModel(
            name="RepositoryOwner",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="User's name.", max_length=32, verbose_name="name"
                    ),
                ),
                (
                    "nickname",
                    models.CharField(
                        help_text="User's or Organization nickname, using letters, numbers, underscores and hyphens without spaces.",
                        max_length=16,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                re.compile("^[-a-zA-Z0-9_]+\\Z"),
                                "Enter a valid 'nickname' consisting of letters, numbers, underscores or hyphens.",
                                "invalid",
                            ),
                            bothub.authentication.models.validate_user_nickname_value,
                        ],
                        verbose_name="nickname",
                    ),
                ),
                (
                    "joined_at",
                    models.DateField(auto_now_add=True, verbose_name="joined at"),
                ),
            ],
            options={"verbose_name": "repository organization"},
        ),
        migrations.RemoveField(model_name="user", name="id"),
        migrations.RemoveField(model_name="user", name="joined_at"),
        migrations.RemoveField(model_name="user", name="name"),
        migrations.RemoveField(model_name="user", name="nickname"),
        migrations.AddField(
            model_name="user",
            name="repository_owner",
            field=models.OneToOneField(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                related_name="user_owner",
                serialize=False,
                to="authentication.RepositoryOwner",
            ),
            preserve_default=False,
        ),
    ]
