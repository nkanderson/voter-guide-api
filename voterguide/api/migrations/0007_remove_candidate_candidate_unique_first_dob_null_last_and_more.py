# Generated by Django 4.1.3 on 2022-11-17 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0006_seat_seat_seat_unique_role_level_null_state_and_more"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="candidate",
            name="candidate_unique_first_dob_null_last",
        ),
        migrations.RemoveConstraint(
            model_name="candidate",
            name="candidate_unique_first_null_dob_last",
        ),
        migrations.AddField(
            model_name="measure",
            name="county",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="candidate",
            name="last_name",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
        migrations.AlterField(
            model_name="candidate",
            name="middle_name",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
    ]