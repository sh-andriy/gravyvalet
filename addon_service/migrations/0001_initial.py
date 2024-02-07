# Generated by Django 4.2.7 on 2024-02-07 20:42

import django.contrib.postgres.fields
import django.db.models.deletion
from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AuthorizedStorageAccount",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(editable=False)),
                ("modified", models.DateTimeField()),
                (
                    "authorized_capabilities",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.IntegerField(
                            choices=[
                                (1, "ACCESS"),
                                (2, "BROWSE"),
                                (3, "UPDATE"),
                                (4, "COMMIT"),
                            ]
                        ),
                        size=None,
                    ),
                ),
                ("default_root_folder", models.CharField(blank=True)),
            ],
            options={
                "verbose_name": "Authorized Storage Account",
                "verbose_name_plural": "Authorized Storage Accounts",
            },
        ),
        migrations.CreateModel(
            name="CredentialsIssuer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(editable=False)),
                ("modified", models.DateTimeField()),
                ("name", models.CharField()),
            ],
            options={
                "verbose_name": "External Service",
                "verbose_name_plural": "External Services",
            },
        ),
        migrations.CreateModel(
            name="ExternalCredentials",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(editable=False)),
                ("modified", models.DateTimeField()),
                ("oauth_key", models.CharField(blank=True, null=True)),
                ("oauth_secret", models.CharField(blank=True, null=True)),
                ("refresh_token", models.CharField(blank=True, null=True)),
                ("date_last_refreshed", models.DateTimeField(blank=True, null=True)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "External Credentials",
                "verbose_name_plural": "External Credentials",
            },
        ),
        migrations.CreateModel(
            name="ResourceReference",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(editable=False)),
                ("modified", models.DateTimeField()),
                ("resource_uri", models.URLField(db_index=True, unique=True)),
            ],
            options={
                "verbose_name": "Resource Reference",
                "verbose_name_plural": "Resource References",
            },
        ),
        migrations.CreateModel(
            name="UserReference",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(editable=False)),
                ("modified", models.DateTimeField()),
                ("user_uri", models.URLField(db_index=True, unique=True)),
            ],
            options={
                "verbose_name": "User Reference",
                "verbose_name_plural": "User References",
            },
        ),
        migrations.CreateModel(
            name="ExternalStorageService",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(editable=False)),
                ("modified", models.DateTimeField()),
                ("max_concurrent_downloads", models.IntegerField()),
                ("max_upload_mb", models.IntegerField()),
                ("auth_uri", models.URLField()),
                (
                    "credentials_issuer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="external_storage_services",
                        to="addon_service.credentialsissuer",
                    ),
                ),
            ],
            options={
                "verbose_name": "External Storage Service",
                "verbose_name_plural": "External Storage Services",
            },
        ),
        migrations.CreateModel(
            name="ExternalAccount",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(editable=False)),
                ("modified", models.DateTimeField()),
                ("remote_account_id", models.CharField()),
                ("remote_account_display_name", models.CharField()),
                (
                    "credentials",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="external_accounts",
                        to="addon_service.externalcredentials",
                    ),
                ),
                (
                    "credentials_issuer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="external_accounts",
                        to="addon_service.credentialsissuer",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="external_accounts",
                        to="addon_service.userreference",
                    ),
                ),
            ],
            options={
                "verbose_name": "External Account",
                "verbose_name_plural": "External Accounts",
            },
        ),
        migrations.CreateModel(
            name="ConfiguredStorageAddon",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(editable=False)),
                ("modified", models.DateTimeField()),
                ("root_folder", models.CharField()),
                (
                    "connected_capabilities",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.IntegerField(
                            choices=[
                                (1, "ACCESS"),
                                (2, "BROWSE"),
                                (3, "UPDATE"),
                                (4, "COMMIT"),
                            ]
                        ),
                        size=None,
                    ),
                ),
                (
                    "authorized_resource",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="configured_storage_addons",
                        to="addon_service.resourcereference",
                    ),
                ),
                (
                    "base_account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="configured_storage_addons",
                        to="addon_service.authorizedstorageaccount",
                    ),
                ),
            ],
            options={
                "verbose_name": "Configured Storage Addon",
                "verbose_name_plural": "Configured Storage Addons",
            },
        ),
        migrations.AddField(
            model_name="authorizedstorageaccount",
            name="external_account",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="authorized_storage_accounts",
                to="addon_service.externalaccount",
            ),
        ),
        migrations.AddField(
            model_name="authorizedstorageaccount",
            name="external_storage_service",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="authorized_storage_accounts",
                to="addon_service.externalstorageservice",
            ),
        ),
    ]
