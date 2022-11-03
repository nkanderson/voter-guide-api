from rest_framework import serializers

from voterguide.api.models import Candidate


class CandidateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Candidate
        fields = ["id", "first_name", "last_name", "party", "date_of_birth"]
