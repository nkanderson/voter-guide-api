from rest_framework import serializers

from voterguide.api.models import (
    Candidate,
    Endorser,
    Measure,
    MeasureEndorsement,
    Seat,
    SeatEndorsement,
)


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
            "running_for_seat",
            "seat",
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


class SeatSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Seat
        fields = [
            "id",
            "level",
            "branch",
            "role",
            "body",
            "district",
            "state",
            "city",
            "county",
            "url",
        ]


class MeasureEndorsementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MeasureEndorsement
        fields = [
            "id",
            "endorser",
            "election_date",
            "url",
            "measure",
            "recommendation",
            "url",
        ]


class SeatEndorsementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SeatEndorsement
        fields = [
            "id",
            "endorser",
            "election_date",
            "url",
            "seat",
            "candidates",
            "url",
        ]
