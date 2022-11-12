from rest_framework import serializers

from voterguide.api.models import Candidate, Endorser, Measure


class CandidateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Candidate
        fields = [
            "id",
            "first_name",
            "middle_name",
            "last_name",
            "party",
            "date_of_birth",
            "url",
        ]


class EndorserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Endorser
        fields = [
            "id",
            "name",
            "abbreviation",
            "url",
        ]


class MeasureSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Measure
        fields = [
            "id",
            "name",
            "description",
            "level",
            "city",
            "state",
            "election_date",
            "passed",
            "url",
        ]
