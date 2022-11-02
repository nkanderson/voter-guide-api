from django.db import models


class Candidate(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120, null=True, blank=True)
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

    def __str__(self):
        return f"{self.full_name()} - {self.get_party_display()}"

    def full_name(self):
        return " ".join(name for name in (self.first_name, self.last_name) if name)
