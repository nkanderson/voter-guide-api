# Generated by Django 4.1.3 on 2022-11-17 17:27

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.functions.text
import localflavor.us.models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0005_measure_measure_measure_unique_name_date_state_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Seat",
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
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "level",
                    models.CharField(
                        choices=[
                            ("F", "Federal"),
                            ("S", "State"),
                            ("C", "City"),
                            ("T", "County"),
                            ("R", "Regional"),
                        ],
                        max_length=1,
                    ),
                ),
                (
                    "branch",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("E", "Executive"),
                            ("J", "Judicial"),
                            ("L", "Legislative"),
                            ("O", "Other"),
                        ],
                        max_length=1,
                    ),
                ),
                ("role", models.CharField(blank=True, max_length=200)),
                (
                    "body",
                    models.CharField(
                        blank=True,
                        choices=[("H", "House of Representatives"), ("S", "Senate")],
                        max_length=1,
                    ),
                ),
                ("district", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("state", localflavor.us.models.USStateField(blank=True, max_length=2)),
                ("city", models.CharField(blank=True, max_length=200)),
                ("county", models.CharField(blank=True, max_length=200)),
            ],
        ),
        migrations.AddConstraint(
            model_name="seat",
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower("role"),
                django.db.models.functions.text.Lower("level"),
                condition=models.Q(("state__isnull", True)),
                name="seat_unique_role_level_null_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="seat",
            constraint=models.CheckConstraint(
                check=models.Q(("level__in", ["F", "S", "C", "T", "R"])),
                name="seat_level_valid",
            ),
        ),
        migrations.AddField(
            model_name="candidate",
            name="running_for_seat",
            field=models.ForeignKey(
                help_text="The seat a candidate is running for.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="api.seat",
            ),
        ),
        migrations.AddField(
            model_name="candidate",
            name="seat",
            field=models.ForeignKey(
                help_text="The seat a candidate is currently holding (if any).",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="incumbent",
                to="api.seat",
            ),
        ),
    ]
