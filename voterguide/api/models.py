from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _
from localflavor.us.models import USStateField
from localflavor.us.us_states import STATE_CHOICES


class Level(models.TextChoices):
    FEDERAL = "F", _("Federal")
    STATE = "S", _("State")
    CITY = "C", _("City")
    COUNTY = "T", _("County")
    REGIONAL = "R", _("Regional")


class Branch(models.TextChoices):
    EXECUTIVE = "E", _("Executive")
    JUDICIAL = "J", _("Judicial")
    LEGISLATIVE = "L", _("Legislative")
    OTHER = "O", _("Other")


class LegislativeBody(models.TextChoices):
    HOUSE = "H", _("House of Representatives")
    SENATE = "S", _("Senate")


class Candidate(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=120)
    middle_name = models.CharField(max_length=120, blank=True, default="")
    last_name = models.CharField(max_length=120, blank=True, default="")
    date_of_birth = models.DateField(null=True)
    PARTIES = (
        ("C", "Constitution"),
        ("D", "Democrat"),
        ("G", "Pacific Green"),
        ("I", "Independent"),
        ("L", "Libertarian"),
        ("N", "No party"),
        ("O", "Other"),
        ("P", "Progressive"),
        ("R", "Republican"),
        ("U", "Unknown"),
        ("W", "Working Families Party"),
    )
    party = models.CharField(choices=PARTIES, default="U", max_length=1)
    running_for_seat = models.ForeignKey(
        "Seat",
        on_delete=models.SET_NULL,
        null=True,
        help_text="The seat a candidate is running for.",
    )
    seat = models.ForeignKey(
        "Seat",
        on_delete=models.SET_NULL,
        null=True,
        related_name="incumbent",
        help_text="The seat a candidate is currently holding (if any).",
    )

    class Meta:
        # TODO: Consider using the FEC candidate ID instead. As described by ID_ID in
        # https://www.fec.gov/campaign-finance-data/candidate-master-file-description/
        # This would require creating new candidate entries if a candidate runs for a
        # different office than the one associated with the ID.
        # The following is probably the best solution for now, as it allows for unique
        # identification without overly constraining to prevent candidates with the same
        # first and last names from being entered.
        # The constraints below offer enough initial specification and flexibility to allow
        # for the following:
        # - Candidates with a date of birth that is not public
        # - Candidates whose names may not conform to "First Last" structure
        # - Disambiguation of candidates with the same name if date of birth is known for one
        constraints = [
            models.UniqueConstraint(
                Lower("first_name"),
                Lower("last_name"),
                "date_of_birth",
                name="candidate_unique_first_last_dob",
            ),
            models.UniqueConstraint(
                Lower("first_name"),
                Lower("last_name"),
                condition=Q(date_of_birth__isnull=True),
                name="candidate_unique_first_last_null_dob",
            ),
        ]

    def __str__(self):
        born = ""
        if self.date_of_birth:
            born = f" (born {self.date_of_birth.strftime('%B %-d, %Y')})"
        return f"{self.full_name()}{born} - {self.get_party_display()}"

    def full_name(self):
        return " ".join(
            name for name in (self.first_name, self.middle_name, self.last_name) if name
        )


class Endorser(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=120)
    abbreviation = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"


class Measure(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    level = models.CharField(max_length=1, choices=Level.choices)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    city = models.CharField(max_length=200, blank=True)
    county = models.CharField(max_length=200, blank=True)
    state = USStateField(choices=STATE_CHOICES)
    election_date = models.DateField()
    passed = models.BooleanField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                "election_date",
                "state",
                name="measure_unique_name_date_state",
            ),
            models.CheckConstraint(
                check=models.Q(level__in=Level.values),
                name="measure_level_valid",
            ),
            models.CheckConstraint(
                check=models.Q(state__in=[state[0] for state in STATE_CHOICES]),
                name="measure_state_valid",
            ),
        ]

    def __str__(self):
        return (
            f"{self.name}: election on {self.election_date.strftime('%B %-d, %Y')} "
            f"in {self.get_state_display()}"
        )


class Seat(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    level = models.CharField(max_length=1, choices=Level.choices)
    branch = models.CharField(max_length=1, choices=Branch.choices, blank=True)
    # Role is similar to title, e.g. President, Mayor, Representative, Justice, Governor
    role = models.CharField(max_length=200, blank=True)
    body = models.CharField(max_length=1, choices=LegislativeBody.choices, blank=True)
    district = models.PositiveSmallIntegerField(null=True, blank=True)
    state = USStateField(choices=STATE_CHOICES, blank=True)
    city = models.CharField(max_length=200, blank=True)
    county = models.CharField(max_length=200, blank=True)

    class Meta:
        constraints = [
            # For federal seats where state is null, role and level must be unique
            # For example, President should not have a state, and should be unique.
            # A federal-level House of Representatives seat may not be unique on
            # these fields, but should have a non-null state value.
            models.UniqueConstraint(
                Lower("role"),
                Lower("level"),
                condition=Q(state__isnull=True),
                name="seat_unique_role_level_null_state",
            ),
            models.CheckConstraint(
                check=models.Q(level__in=Level.values),
                name="seat_level_valid",
            ),
        ]

    def __str__(self):
        district_str = ""
        if self.district:
            district_str = f", district {self.district},"
        city_str = ""
        if self.city:
            city_str = f" in the city of {self.city}"
        county_str = ""
        if self.county:
            county_str = f" in {self.county} County"
        state_str = ""
        if self.state:
            state_str = f" in the state of {self.get_state_display()}"
        return (
            f"{self.role} at the {self.get_level_display()} level"
            f"{district_str}{city_str}{county_str}{state_str}"
        )

    def validate_unique(self, *args, **kwargs):
        # Check that provided data represents a unique seat
        if self.__class__.objects.filter(
            level=self.level,
            branch=self.branch,
            role=self.role,
            body=self.body,
            district=self.district,
            state=self.state,
            county=self.county,
            city=self.city,
        ).exists():
            raise ValidationError(
                f"Seat must be unique at the provided level of {self.level}"
            )
        return super().validate_unique(*args, **kwargs)

    def clean(self, *args, **kwargs):
        # Set default role or raise if it isn't set and can't be determined
        if not self.role:
            match self.body:
                case "H":
                    self.role = "Representative"
                case "S":
                    self.role = "Senator"
                case _:
                    raise ValidationError(
                        "Role could not be determined and must be set explicitly."
                    )

        # If state is not blank, check that it is valid
        if self.state and self.state not in (
            state_codes := [state[0] for state in STATE_CHOICES]
        ):
            raise ValidationError(
                f"State value is invalid. Must be one of {', '.join(state_codes)}"
            )

        # If body is not blank, check that it is valid
        if self.body and self.body not in (valid_bodies := LegislativeBody.values):
            raise ValidationError(
                f"Body value is invalid. Must be one of {', '.join(valid_bodies)}"
            )

        # For roles not at the Federal level, state must be set, and location field matching
        # level should also be set
        if self.level != "F":
            if not self.state:
                raise ValidationError(
                    "State field must be set for all non-Federal roles."
                )

            if self.level == "C" and not self.city:
                raise ValidationError(
                    "City field must be set for seats with level of City."
                )

            if self.level == "T" and not self.county:
                raise ValidationError(
                    "County field must be set for seats with level of County."
                )

        # Check that the state and legislative body is set for legislative branch seats
        if self.branch == "L":
            if not self.state:
                raise ValidationError(
                    "State field must be set for all seats in the legislature."
                )

            if not self.body:
                raise ValidationError(
                    "Body field must be set for all seats in the legislature."
                )

        # Check that district is set for any seat in a House of Representatives,
        # and any state senator
        if (
            self.body == "H" or (self.body == "S" and self.level == "S")
        ) and not self.district:
            raise ValidationError(
                "District field must be set for all seats in the House of Representatives,",
                " and all state senators.",
            )

        super().clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
