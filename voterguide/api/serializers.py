from rest_framework import serializers

from voterguide.api.models import Candidate, Endorser


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
