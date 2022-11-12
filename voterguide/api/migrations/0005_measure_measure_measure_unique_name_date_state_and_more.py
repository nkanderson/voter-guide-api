# Generated by Django 4.1.3 on 2022-11-11 23:11

from django.db import migrations, models
import django.db.models.functions.text
import localflavor.us.models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0004_endorser"),
    ]

    operations = [
        migrations.CreateModel(
            name="Measure",
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
                ("name", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True)),
                ("city", models.CharField(blank=True, max_length=200)),
                ("state", localflavor.us.models.USStateField(max_length=2)),
                ("election_date", models.DateField()),
                ("passed", models.BooleanField(null=True)),
            ],
        ),
        migrations.AddConstraint(
            model_name="measure",
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower("name"),
                models.F("election_date"),
                models.F("state"),
                name="measure_unique_name_date_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="measure",
            constraint=models.CheckConstraint(
                check=models.Q(("level__in", ["F", "S", "C", "T", "R"])),
                name="measure_level_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="measure",
            constraint=models.CheckConstraint(
                check=models.Q(
                    (
                        "state__in",
                        [
                            "AL",
                            "AK",
                            "AS",
                            "AZ",
                            "AR",
                            "AA",
                            "AE",
                            "AP",
                            "CA",
                            "CO",
                            "CT",
                            "DE",
                            "DC",
                            "FL",
                            "GA",
                            "GU",
                            "HI",
                            "ID",
                            "IL",
                            "IN",
                            "IA",
                            "KS",
                            "KY",
                            "LA",
                            "ME",
                            "MD",
                            "MA",
                            "MI",
                            "MN",
                            "MS",
                            "MO",
                            "MT",
                            "NE",
                            "NV",
                            "NH",
                            "NJ",
                            "NM",
                            "NY",
                            "NC",
                            "ND",
                            "MP",
                            "OH",
                            "OK",
                            "OR",
                            "PA",
                            "PR",
                            "RI",
                            "SC",
                            "SD",
                            "TN",
                            "TX",
                            "UT",
                            "VT",
                            "VI",
                            "VA",
                            "WA",
                            "WV",
                            "WI",
                            "WY",
                        ],
                    )
                ),
                name="measure_state_valid",
            ),
        ),
    ]