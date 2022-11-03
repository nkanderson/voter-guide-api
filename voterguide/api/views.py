from rest_framework import viewsets

from voterguide.api.models import Candidate
from voterguide.api.serializers import CandidateSerializer


class CandidateViewSet(viewsets.ModelViewSet):
    """
    This viewset provides `list`, `create`, `retrieve`, `update` and `destroy` actions.
    """

    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
