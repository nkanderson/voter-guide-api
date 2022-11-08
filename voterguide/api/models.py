from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower


class Candidate(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=120)
    middle_name = models.CharField(max_length=120, null=True, blank=True)
    last_name = models.CharField(max_length=120, null=True, blank=True)
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
            models.UniqueConstraint(
                Lower("first_name"),
                "date_of_birth",
                condition=Q(last_name__isnull=True),
                name="candidate_unique_first_dob_null_last",
            ),
            models.UniqueConstraint(
                Lower("first_name"),
                condition=Q(date_of_birth__isnull=True) & Q(last_name__isnull=True),
                name="candidate_unique_first_null_dob_last",
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
